"""
AI extraction service combining OpenAI GPT-4 and AWS Textract

Two-Phase Extraction:
- Phase 1: Base ACORD 125 extraction + coverage detection
- Phase 2: Form-specific extraction (ACORD 126, 130, 140) based on detected coverages
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

from app.services.openai_service import openai_service
from app.services.textract_service import textract_service
from app.services.s3_service import s3_service
from app.core.acord_schema import ACORD125Schema, create_acord_schema_from_extraction
from app.config import settings
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

# Coverage type to ACORD form mapping
COVERAGE_TO_FORM_MAP = {
    "COMMERCIAL_GENERAL_LIABILITY": "ACORD_126",
    "WORKERS_COMPENSATION": "ACORD_130",
    "COMMERCIAL_PROPERTY": "ACORD_140",
    "BUSINESS_AUTO": "ACORD_127",
    "MOTOR_CARRIER": "ACORD_127",
    "TRUCKERS": "ACORD_127",
}


class AIExtractionService:
    """Main service for AI-powered data extraction"""
    
    def __init__(self):
        """Initialize AI extraction service"""
        self.openai_service = openai_service
        self.textract_service = textract_service
        self.s3_service = s3_service
    
    async def extract_from_documents(
        self, 
        submission_id: str,
        document_keys: List[str],
        user_id: str,
        confidence_threshold: float = 0.7,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from multiple documents
        
        Args:
            submission_id: Unique submission identifier
            document_keys: List of S3 keys for uploaded documents
            user_id: User identifier
            confidence_threshold: Minimum confidence for extracted data
            progress_callback: Optional callback function to report progress (accepts int 0-100)
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        try:
            logger.info(f"=== Starting AI extraction for submission {submission_id} ===")
            logger.info(f"Documents to process: {len(document_keys)}")
            for i, key in enumerate(document_keys):
                logger.info(f"  Document {i+1}: {key}")
            
            # Step 1: Extract text from all documents using Textract (20-40%)
            extracted_texts = []
            document_metadata = []
            
            total_documents = len(document_keys)
            for idx, key in enumerate(document_keys):
                logger.info(f"=== Processing document {idx + 1}/{total_documents}: {key} ===")
                
                # Determine document type from file extension
                file_extension = key.split('.')[-1].lower()
                document_type = self._get_document_type(file_extension)
                logger.info(f"Document type detected: {document_type} (extension: {file_extension})")
                
                # Report progress before starting Textract (each doc spans a portion of 20-40%)
                if progress_callback:
                    pre_progress = 20 + int(idx / total_documents * 18)
                    progress_callback(pre_progress)
                    logger.info(f"Pre-Textract progress: {pre_progress}%")
                
                # Extract text using Textract
                try:
                    logger.info(f"Calling Textract for document: s3://{settings.AWS_S3_BUCKET}/{key}")
                    textract_result = await run_in_threadpool(
                        self.textract_service.extract_text_from_s3,
                        bucket=settings.AWS_S3_BUCKET,
                        key=key,
                        document_type=document_type
                    )
                    logger.info(f"Textract completed for {key} - extracted {len(textract_result.get('text', ''))} chars")
                except Exception as textract_error:
                    logger.error(f"Textract FAILED for document {key}: {str(textract_error)}", exc_info=True)
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Document text extraction failed for {key.split('/')[-1]}: {str(textract_error)}"
                    )
                
                extracted_texts.append(textract_result['text'])
                document_metadata.append({
                    'key': key,
                    'type': document_type,
                    'page_count': textract_result.get('page_count', 1),
                    'confidence_scores': textract_result.get('confidence_scores', {}),
                    'extraction_status': textract_result.get('status', 'completed')
                })
                
                # Report progress after each document (20-40% range)
                if progress_callback:
                    progress = 20 + int((idx + 1) / total_documents * 20)
                    progress_callback(progress)
                    logger.info(f"Textract progress: {progress}% (completed {idx+1}/{total_documents} documents)")
            
            # Step 2: Combine all extracted text
            combined_text = '\n\n--- DOCUMENT SEPARATOR ---\n\n'.join(extracted_texts)
            logger.info(f"Combined text from {total_documents} document(s)")
            
            # Step 3: Extract structured data using OpenAI (40-60%)
            if progress_callback:
                progress_callback(45)
            
            logger.info("Extracting structured data using OpenAI GPT-4")
            extracted_data = await run_in_threadpool(
                self.openai_service.extract_insurance_data,
                extracted_text=combined_text,
                file_type="combined",
                confidence_threshold=confidence_threshold
            )
            
            if progress_callback:
                progress_callback(50)
                logger.info("Phase 1 extraction complete: 50%")
            
            # Step 4: PHASE 2 - Form-specific extraction based on detected coverages (50-70%)
            logger.info("Starting Phase 2: Form-specific extraction")
            
            # Detect which coverages are present
            detected_coverages = self.openai_service.detect_coverages_from_extraction(extracted_data)
            logger.info(f"Detected coverages for Phase 2: {detected_coverages}")
            
            # Run form-specific extractions for detected coverages
            form_specific_data = {}
            if detected_coverages:
                if progress_callback:
                    progress_callback(55)
                
                form_specific_data = await self._run_phase2_extractions(
                    combined_text,
                    extracted_data,
                    detected_coverages,
                    confidence_threshold,
                    progress_callback
                )
                
                # Merge form-specific data into extracted_data
                extracted_data = self._merge_extraction_results(extracted_data, form_specific_data)
            
            if progress_callback:
                progress_callback(70)
                logger.info("Phase 2 extraction complete: 70%")
            
            # Step 5: Generate risk narrative (70-75%)
            logger.info("Generating risk narrative")
            risk_narrative = await run_in_threadpool(
                self.openai_service.generate_risk_narrative,
                extracted_data
            )
            
            if progress_callback:
                progress_callback(75)
                logger.info("Risk narrative generated: 75%")
            
            # Step 7: Convert to ACORD 125 schema (75-85%)
            if progress_callback:
                progress_callback(78)
            
            logger.info("Converting extracted data to ACORD 125 schema")
            acord_schema = create_acord_schema_from_extraction(extracted_data)
            acord_schema.risk_narrative = risk_narrative
            acord_schema.extraction_timestamp = datetime.utcnow().isoformat()
            acord_schema.validation_status = 'extracted'
            
            if progress_callback:
                progress_callback(85)
                logger.info("ACORD schema conversion complete: 85%")
            
            # Step 8: Prepare final result
            extraction_result = {
                'submission_id': submission_id,
                'user_id': user_id,
                'extraction_timestamp': datetime.utcnow().isoformat(),
                'status': 'completed',
                'confidence_threshold': confidence_threshold,
                'extracted_data': extracted_data,
                'acord_schema': acord_schema.to_dict(),
                'risk_narrative': risk_narrative,
                'document_metadata': document_metadata,
                'detected_coverages': detected_coverages,
                'form_specific_extractions': list(form_specific_data.keys()) if form_specific_data else [],
                'processing_stats': {
                    'total_documents': len(document_keys),
                    'total_pages': sum(doc['page_count'] for doc in document_metadata),
                    'average_confidence': self._calculate_average_confidence(document_metadata),
                    'extraction_method': 'openai_gpt4_textract_two_phase',
                    'phase1_fields': 'ACORD_125',
                    'phase2_forms': list(form_specific_data.keys()) if form_specific_data else [],
                    'completion_percentage': 100.0,
                    'missing_fields': []
                }
            }
            
            logger.info(f"AI extraction completed for submission {submission_id}")
            return extraction_result
            
        except Exception as e:
            logger.error(f"AI extraction failed for submission {submission_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")
    
    def _get_document_type(self, file_extension: str) -> str:
        """Map file extension to document type"""
        extension_map = {
            'pdf': 'pdf',
            'jpg': 'image',
            'jpeg': 'image',
            'png': 'image',
            'tiff': 'image',
            'docx': 'pdf',  # Treat DOCX as PDF for Textract
            'doc': 'pdf'
        }
        return extension_map.get(file_extension.lower(), 'pdf')
    
    def _calculate_average_confidence(self, document_metadata: List[Dict[str, Any]]) -> float:
        """Calculate average confidence across all documents"""
        total_confidence = 0.0
        total_documents = 0
        
        for doc in document_metadata:
            confidence_scores = doc.get('confidence_scores', {})
            avg_line_conf = confidence_scores.get('average_line_confidence', 0.0)
            if avg_line_conf > 0:
                total_confidence += avg_line_conf
                total_documents += 1
        
        return total_confidence / total_documents if total_documents > 0 else 0.0
    
    def validate_extracted_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean extracted data
        
        Args:
            extracted_data: Raw extracted data from OpenAI
            
        Returns:
            Validated and cleaned data
        """
        try:
            validated_data = {}
            
            # Validate each category
            for category, fields in extracted_data.items():
                validated_category = {}
                
                for field_name, field_data in fields.items():
                    if isinstance(field_data, dict) and 'value' in field_data:
                        validated_field = self._validate_field(field_name, field_data)
                        validated_category[field_name] = validated_field
                    else:
                        validated_category[field_name] = field_data
                
                validated_data[category] = validated_category
            
            return validated_data
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data validation failed: {str(e)}")
    
    def _validate_field(self, field_name: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual field data"""
        value = field_data.get('value')
        confidence = field_data.get('confidence', 0.0)
        
        # Apply field-specific validation
        if field_name in ['effective_date', 'expiration_date']:
            validated_value = self._validate_date(value)
        elif field_name in ['premium_amount', 'annual_revenue', 'number_of_employees', 'years_in_business']:
            validated_value = self._validate_number(value)
        elif field_name in ['phone', 'broker_phone']:
            validated_value = self._validate_phone(value)
        elif field_name in ['email', 'broker_email']:
            validated_value = self._validate_email(value)
        elif field_name == 'state':
            validated_value = self._validate_state(value)
        else:
            validated_value = self._validate_text(value)
        
        return {
            'value': validated_value,
            'confidence': confidence,
            'original_value': value,
            'validation_status': 'validated'
        }
    
    def _validate_date(self, value: Any) -> Optional[str]:
        """Validate and format date"""
        if not value:
            return None
        
        try:
            # Try to parse common date formats
            from datetime import datetime
            
            if isinstance(value, str):
                # Remove common prefixes/suffixes
                clean_value = value.strip().lower()
                if 'effective' in clean_value or 'expiration' in clean_value:
                    # Extract date part
                    import re
                    date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', clean_value)
                    if date_match:
                        value = date_match.group()
                
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y']:
                    try:
                        parsed_date = datetime.strptime(value, fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            
            return None
        except Exception:
            return None
    
    def _validate_number(self, value: Any) -> Optional[float]:
        """Validate and convert to number"""
        if not value:
            return None
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            if isinstance(value, str):
                # Remove currency symbols and commas
                import re
                clean_value = re.sub(r'[^\d.]', '', value)
                if clean_value:
                    return float(clean_value)
            
            return None
        except (ValueError, TypeError):
            return None
    
    def _validate_phone(self, value: Any) -> Optional[str]:
        """Validate phone number format"""
        if not value:
            return None
        
        try:
            if isinstance(value, str):
                # Remove all non-digit characters
                import re
                digits = re.sub(r'\D', '', value)
                
                # Check if it looks like a phone number
                if len(digits) >= 10:
                    # Format as (XXX) XXX-XXXX
                    if len(digits) == 10:
                        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                    elif len(digits) == 11 and digits[0] == '1':
                        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
                    else:
                        return value  # Return original if can't format
            
            return None
        except Exception:
            return None
    
    def _validate_email(self, value: Any) -> Optional[str]:
        """Validate email format"""
        if not value:
            return None
        
        try:
            if isinstance(value, str):
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if re.match(email_pattern, value.strip()):
                    return value.strip().lower()
            
            return None
        except Exception:
            return None
    
    def _validate_state(self, value: Any) -> Optional[str]:
        """Validate state abbreviation"""
        if not value:
            return None
        
        try:
            if isinstance(value, str):
                # US state abbreviations
                state_abbreviations = {
                    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
                    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
                    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
                    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
                    'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
                    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
                    'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
                    'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
                    'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
                    'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
                    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
                    'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
                    'wisconsin': 'WI', 'wyoming': 'WY'
                }
                
                clean_value = value.strip().lower()
                
                # Check if it's already an abbreviation
                if clean_value.upper() in state_abbreviations.values():
                    return clean_value.upper()
                
                # Check if it's a full state name
                if clean_value in state_abbreviations:
                    return state_abbreviations[clean_value]
            
            return None
        except Exception:
            return None
    
    def _validate_text(self, value: Any) -> Optional[str]:
        """Validate text field"""
        if not value:
            return None
        
        try:
            if isinstance(value, str):
                return value.strip()
            
            return str(value).strip()
        except Exception:
            return None
    
    # =========================================================================
    # Phase 2: Form-Specific Extraction Methods
    # =========================================================================
    
    async def _run_phase2_extractions(
        self,
        combined_text: str,
        base_extracted_data: Dict[str, Any],
        detected_coverages: List[str],
        confidence_threshold: float,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Run Phase 2 form-specific extractions based on detected coverages.
        Runs extractions in parallel for efficiency.
        
        Args:
            combined_text: Combined text from all documents
            base_extracted_data: Data extracted in Phase 1
            detected_coverages: List of detected coverage types
            confidence_threshold: Minimum confidence threshold
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping form type to extracted data
        """
        form_specific_data = {}
        extraction_tasks = []
        
        # Determine which forms to extract based on detected coverages
        forms_to_extract = []
        for coverage in detected_coverages:
            form_type = COVERAGE_TO_FORM_MAP.get(coverage)
            if form_type and form_type not in forms_to_extract:
                forms_to_extract.append((coverage, form_type))
        
        if not forms_to_extract:
            logger.info("No form-specific extractions needed")
            return form_specific_data
        
        logger.info(f"Running Phase 2 extraction for forms: {[f[1] for f in forms_to_extract]}")
        
        # Create extraction tasks for parallel execution
        for coverage, form_type in forms_to_extract:
            if form_type == "ACORD_126":
                task = run_in_threadpool(
                    self.openai_service.extract_acord126_data,
                    combined_text,
                    base_extracted_data,
                    confidence_threshold
                )
                extraction_tasks.append((form_type, task))
            
            elif form_type == "ACORD_130":
                task = run_in_threadpool(
                    self.openai_service.extract_acord130_data,
                    combined_text,
                    base_extracted_data,
                    confidence_threshold
                )
                extraction_tasks.append((form_type, task))
            
            elif form_type == "ACORD_140":
                task = run_in_threadpool(
                    self.openai_service.extract_acord140_data,
                    combined_text,
                    base_extracted_data,
                    confidence_threshold
                )
                extraction_tasks.append((form_type, task))
            
            elif form_type == "ACORD_127":
                task = run_in_threadpool(
                    self.openai_service.extract_acord127_data,
                    combined_text,
                    base_extracted_data,
                    confidence_threshold
                )
                extraction_tasks.append((form_type, task))
        
        # Execute all tasks in parallel
        if extraction_tasks:
            # Update progress
            if progress_callback:
                progress_callback(58)
            
            # Run all extractions concurrently
            results = await asyncio.gather(
                *[task for _, task in extraction_tasks],
                return_exceptions=True
            )
            
            # Process results
            for i, (form_type, _) in enumerate(extraction_tasks):
                result = results[i]
                if isinstance(result, Exception):
                    logger.error(f"Phase 2 extraction failed for {form_type}: {str(result)}")
                    form_specific_data[form_type] = {}
                else:
                    form_specific_data[form_type] = result
                    logger.info(f"Phase 2 extraction complete for {form_type}")
            
            # Update progress
            if progress_callback:
                progress_callback(65)
        
        return form_specific_data
    
    def _merge_extraction_results(
        self,
        base_data: Dict[str, Any],
        form_specific_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge form-specific extraction results into the base extracted data.
        
        Args:
            base_data: Base extraction data from Phase 1
            form_specific_data: Form-specific data from Phase 2
            
        Returns:
            Merged extraction data
        """
        merged = base_data.copy()
        
        # Add form-specific sections
        for form_type, data in form_specific_data.items():
            if not data:
                continue
            
            if form_type == "ACORD_126" and "general_liability" in data:
                merged["general_liability"] = data["general_liability"]
                logger.info("Merged ACORD 126 (GL) data into extraction results")
            
            elif form_type == "ACORD_130" and "workers_compensation" in data:
                merged["workers_compensation"] = data["workers_compensation"]
                logger.info("Merged ACORD 130 (WC) data into extraction results")
            
            elif form_type == "ACORD_140" and "property" in data:
                merged["property"] = data["property"]
                logger.info("Merged ACORD 140 (Property) data into extraction results")
            
            elif form_type == "ACORD_127" and "commercial_auto" in data:
                merged["commercial_auto"] = data["commercial_auto"]
                logger.info("Merged ACORD 127 (Commercial Auto) data into extraction results")
        
        return merged


# Global AI extraction service instance
ai_extraction_service = AIExtractionService()
