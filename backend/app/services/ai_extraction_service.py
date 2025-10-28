"""
AI extraction service combining OpenAI GPT-4 and AWS Textract
"""

import json
import logging
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
            logger.info(f"Starting AI extraction for submission {submission_id}")
            
            # Step 1: Extract text from all documents using Textract (20-40%)
            extracted_texts = []
            document_metadata = []
            
            total_documents = len(document_keys)
            for idx, key in enumerate(document_keys):
                logger.info(f"Processing document {idx + 1}/{total_documents}: {key}")
                
                # Determine document type from file extension
                file_extension = key.split('.')[-1].lower()
                document_type = self._get_document_type(file_extension)
                
                # Extract text using Textract
                textract_result = await run_in_threadpool(
                    self.textract_service.extract_text_from_s3,
                    bucket=settings.AWS_S3_BUCKET,
                    key=key,
                    document_type=document_type
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
                    logger.info(f"Textract progress: {progress}%")
            
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
                progress_callback(55)
                logger.info("OpenAI extraction complete: 55%")
            
            # Step 4: Generate risk narrative (60-70%)
            if progress_callback:
                progress_callback(60)
            
            logger.info("Generating risk narrative")
            risk_narrative = await run_in_threadpool(
                self.openai_service.generate_risk_narrative,
                extracted_data
            )
            
            if progress_callback:
                progress_callback(70)
                logger.info("Risk narrative generated: 70%")
            
            # Step 5: Convert to ACORD 125 schema (70-85%)
            if progress_callback:
                progress_callback(75)
            
            logger.info("Converting extracted data to ACORD 125 schema")
            acord_schema = create_acord_schema_from_extraction(extracted_data)
            acord_schema.risk_narrative = risk_narrative
            acord_schema.extraction_timestamp = datetime.utcnow().isoformat()
            acord_schema.validation_status = 'extracted'
            
            if progress_callback:
                progress_callback(85)
                logger.info("ACORD schema conversion complete: 85%")
            
            # Step 6: Prepare final result
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
                'processing_stats': {
                    'total_documents': len(document_keys),
                    'total_pages': sum(doc['page_count'] for doc in document_metadata),
                    'average_confidence': self._calculate_average_confidence(document_metadata),
                    'extraction_method': 'openai_gpt4_textract',
                    'completion_percentage': 100.0,  # TODO: Calculate actual completion percentage
                    'missing_fields': []  # TODO: Calculate actual missing fields
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


# Global AI extraction service instance
ai_extraction_service = AIExtractionService()
