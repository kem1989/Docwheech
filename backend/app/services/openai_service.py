"""
OpenAI service for AI-powered data extraction
"""

import openai
import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI GPT-4 integration"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not provided - AI service will be disabled")
            self.client = None
            return
            
        try:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.client = None
    
    def extract_insurance_data(
        self, 
        extracted_text: str, 
        file_type: str,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Extract structured insurance data from text using GPT-4
        
        Args:
            extracted_text: Raw text extracted from documents
            file_type: Type of document (pdf, docx, xlsx, etc.)
            confidence_threshold: Minimum confidence score for extracted data
            
        Returns:
            Dictionary containing extracted data with confidence scores
        """
        if not self.client:
            raise HTTPException(status_code=503, detail="OpenAI service not available")
        
        try:
            # Create the extraction prompt
            prompt = self._create_extraction_prompt(extracted_text, file_type)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance data extraction specialist. Extract structured data from insurance documents and return it in the specified JSON format with confidence scores."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Validate and filter by confidence threshold
            filtered_data = self._filter_by_confidence(extracted_data, confidence_threshold)
            
            logger.info(f"Successfully extracted data from {file_type} document")
            return filtered_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to parse AI extraction response")
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")
    
    def _create_extraction_prompt(self, text: str, file_type: str) -> str:
        """Create the enhanced extraction prompt for OpenAI with 30+ critical fields"""
        # Use larger text limit for multi-document submissions (GPT-4-turbo supports 128K tokens)
        text_limit = 50000
        return f"""
Extract ACORD 125 Commercial Insurance Application data from the following {file_type.upper()} document text and return it in the specified JSON format.

IMPORTANT: This submission may contain MULTIPLE DOCUMENTS separated by "--- DOCUMENT SEPARATOR ---".
- Documents may appear in ANY ORDER - do not assume the first document is the main application
- The main insurance application/quote request contains: business name, contact info, coverage requests, effective dates, prior carrier info
- Supporting documents may include: financial statements, loss runs, property schedules
- YOU MUST SEARCH ALL DOCUMENTS THOROUGHLY for each field before returning null
- DO NOT return null for fields that ARE present in the text - search the ENTIRE text across all document sections

Document Text:
{text[:text_limit]}

Please extract the following ACORD 125 information and return it as a JSON object with confidence scores (0.0 to 1.0):

{{
    "agency": {{
        "name": {{"value": "agency name or null", "confidence": 0.0-1.0}},
        "code": {{"value": "agency code or null", "confidence": 0.0-1.0}},
        "address": {{"value": "agency address or null", "confidence": 0.0-1.0}},
        "phone": {{"value": "agency phone or null", "confidence": 0.0-1.0}},
        "email": {{"value": "agency email or null", "confidence": 0.0-1.0}}
    }},
    "transaction_status": {{
        "type": {{"value": "QUOTE, RENEW, ISSUE_POLICY, BOUND, CANCEL, CHANGE or null", "confidence": 0.0-1.0}},
        "bound_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
        "bound_time": {{"value": "HH:MM AM/PM or null", "confidence": 0.0-1.0}}
    }},
    "policy": {{
        "proposed_effective_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
        "proposed_expiration_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
        "billing_plan": {{"value": "DIRECT, AGENCY or null", "confidence": 0.0-1.0}},
        "deposit_premium": {{"value": "deposit premium amount or null", "confidence": 0.0-1.0}},
        "minimum_premium": {{"value": "minimum premium or null", "confidence": 0.0-1.0}}
    }},
    "coverage_requested": {{
        "value": [
            "EXPLICITLY stated coverage requests from the document. Look for phrases like 'Coverage Requested:', 'Coverages Needed:', 'Quote for:', 'Apply for:', 'Insurance Needed:', checkbox selections. Return the EXACT coverages mentioned or empty array [] if not explicitly stated."
        ],
        "confidence": 0.0-1.0,
        "source": "EXPLICIT or INFERRED - use EXPLICIT only if coverage is directly stated/checked in the document"
    }},
    "lines_of_business": {{
        "value": [
            "ONLY select from these ENUM values based on the business operations described in the document: COMMERCIAL_GENERAL_LIABILITY, COMMERCIAL_PROPERTY, BUSINESS_AUTO, UMBRELLA, BUSINESS_OWNERS, GARAGE_AND_DEALERS, CRIME, BOILER_AND_MACHINERY, COMMERCIAL_INLAND_MARINE, CYBER_AND_PRIVACY, FIDUCIARY_LIABILITY, LIQUOR_LIABILITY, MOTOR_CARRIER, TRUCKERS, YACHT, WORKERS_COMPENSATION. If none apply, return an empty array []"
        ],
        "confidence": 0.0-1.0
    }},
    "first_named_insured": {{
        "name": {{"value": "legal business name or null", "confidence": 0.0-1.0}},
        "mailing_address": {{"value": "mailing address or null", "confidence": 0.0-1.0}},
        "business_structure": {{"value": "INDIVIDUAL, LLC, CORPORATION, PARTNERSHIP, etc. or null", "confidence": 0.0-1.0}},
        "naics_code": {{"value": "6-digit NAICS code or null", "confidence": 0.0-1.0}},
        "sic_code": {{"value": "SIC code or null", "confidence": 0.0-1.0}},
        "fein_or_ssn": {{"value": "FEIN/SSN or null", "confidence": 0.0-1.0}},
        "business_phone": {{"value": "phone or null", "confidence": 0.0-1.0}},
        "website_address": {{"value": "website URL or null", "confidence": 0.0-1.0}}
    }},
    "other_named_insureds": {{
        "value": ["list of additional named insured objects with name, mailing address, business structure, number of members/managers if LLC, naics_code, sic_code, fein_or_ssn, business_phone, website_address or null"],
        "confidence": 0.0-1.0
    }},
    "contacts": {{
        "value": ["list of contact objects with type, name, email, phone or null"],
        "confidence": 0.0-1.0
    }},
    "nature_of_business": {{
        "date_business_started": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
        "business_type": {{"value": ["array of business type strings like 'manufacturing', 'retail', 'wholesale', etc. or empty array []"], "confidence": 0.0-1.0}},
        "description_of_primary_operations": {{"value": "primary operations description or null", "confidence": 0.0-1.0}},
        "retail_stores_or_service_operations": {{"value": "true/false or null", "confidence": 0.0-1.0}},
        "installation_service_repair_work_percent": {{"value": "percentage (0-100) of installation service or repair work or null", "confidence": 0.0-1.0}},
        "off_premises_installation_service_repair_percent": {{"value": "percentage (0-100) of off premises installation service or repair work or null", "confidence": 0.0-1.0}},
        "description_of_operations_other_named_insureds": {{"value": "description of operations for other named insureds or null", "confidence": 0.0-1.0}}
    }},
    "premises": {{
        "value": ["list of premise objects with street address, city, state, zip, operations description, full time employees, part time employees, revenues, square footage, interest (OWNER or TENANT), any area leased to others (Yes/No) or null"],
        "confidence": 0.0-1.0
    }},
    "prior_carriers": {{
        "value": ["list of prior carrier objects with carrier name, policy number, effective/expiration dates, premium or null"],
        "confidence": 0.0-1.0
    }},
    "loss_history": {{
        "has_losses": {{"value": "true/false or null", "confidence": 0.0-1.0}},
        "losses": {{"value": ["list of loss objects with date, description, amounts paid/reserved or null"], "confidence": 0.0-1.0}}
    }}
}}

CRITICAL INSTRUCTIONS:
1. THOROUGHLY SEARCH the entire text for each field - data may appear in any document section
2. Use null ONLY for information that is genuinely NOT present in any document
3. For dates, convert ANY date format to YYYY-MM-DD (e.g., "January 15, 2018" -> "2018-01-15", "March 1, 2024" -> "2024-03-01")
4. For numbers, extract only numeric values (no currency symbols)
5. For business structure, use ENUM values: INDIVIDUAL, LLC, CORPORATION, PARTNERSHIP, JOINT_VENTURE, NOT_FOR_PROFIT_ORG, SUBCHAPTER_S_CORPORATION, TRUST
6. For transaction type, map common phrases:
   - "Renewal Quote", "Renewal", "Renew" -> RENEWAL
   - "New Quote", "Quote", "New Business" -> QUOTE  
   - "Issue", "Issue Policy" -> ISSUE_POLICY
   - "Bound" -> BOUND
   - "Cancel" -> CANCEL
   - "Change", "Endorsement" -> CHANGE
7. Coverage Requested rules (IMPORTANT - TWO-TIER DETECTION):
   - TIER 1 (coverage_requested field): Look for EXPLICIT coverage requests - checkboxes marked, phrases like "Coverage Requested:", "Coverages Needed:", "Quote for:", "Apply for:"
   - If explicit coverage requests are found, populate coverage_requested with source="EXPLICIT"
   - If NO explicit coverage requests found, leave coverage_requested empty or set source="INFERRED"
   
8. Lines of Business rules:
   - STRICTLY select ONLY from: COMMERCIAL_GENERAL_LIABILITY, COMMERCIAL_PROPERTY, BUSINESS_AUTO, UMBRELLA, BUSINESS_OWNERS, GARAGE_AND_DEALERS, CRIME, BOILER_AND_MACHINERY, COMMERCIAL_INLAND_MARINE, CYBER_AND_PRIVACY, FIDUCIARY_LIABILITY, LIQUOR_LIABILITY, MOTOR_CARRIER, TRUCKERS, YACHT, WORKERS_COMPENSATION
   - This field captures what coverages are INDICATED by the business type and operations
   - Use prior carriers as supporting context for what coverages the business typically needs
9. For business_type, extract as ARRAY of strings (e.g., ["manufacturing", "wholesale", "retail"]). Derive from industry descriptions or explicit business classifications in the text.
10. For premises interest field, use ENUM values: OWNER or TENANT
11. For premises "any area leased to others" field, extract as boolean (true/false) or Yes/No (convert Yes to true, No to false)
12. For other_named_insureds business_structure, use the same ENUM values as first_named_insured
13. For nature_of_business installation_service_repair_work_percent and off_premises_installation_service_repair_percent, extract as numeric percentage values (0-100), not boolean. Extract the actual percentage if stated in the document, otherwise use null.
14. Assign confidence scores based on how clearly information is stated - if data is present, confidence should be >= 0.8
15. If information is ambiguous or unclear, assign lower confidence (<0.7)
16. Return only valid JSON format
17. For arrays (lines_of_business, coverage_requested, contacts, premises, other_named_insureds, business_type, etc.), return empty array [] ONLY if no data found
18. NAICS codes must be 6 digits
19. Phone numbers should be in format: (XXX) XXX-XXXX

MULTI-DOCUMENT EXTRACTION REMINDERS:
- "Date Business Started" often appears in the main application - look for phrases like "Date Business Started:", "Established:", "Since:", "Years in Business"
- "Primary Contact" information is usually in the main application header - extract name, phone, email
- "Coverage Type" or "Transaction Type" indicates RENEWAL, QUOTE, etc. - look for "Coverage Type:", "Transaction Type:", "Renewal Quote", etc.
- "Policy Number" for prior carriers often appears with "Current Policy Number:", "Policy #:", etc.
- "Requested Effective Date" or "Proposed Effective Date" indicates when coverage should start
"""
    
    def _filter_by_confidence(
        self, 
        extracted_data: Dict[str, Any], 
        threshold: float
    ) -> Dict[str, Any]:
        """Filter extracted data by confidence threshold"""
        filtered_data = {}
        
        for category, fields in extracted_data.items():
            filtered_category = {}
            for field_name, field_data in fields.items():
                if isinstance(field_data, dict) and 'confidence' in field_data:
                    if field_data['confidence'] >= threshold:
                        filtered_category[field_name] = field_data
                    else:
                        # Include low confidence data but mark it
                        filtered_category[field_name] = {
                            'value': field_data.get('value'),
                            'confidence': field_data['confidence'],
                            'low_confidence': True
                        }
                else:
                    filtered_category[field_name] = field_data
            
            filtered_data[category] = filtered_category
        
        return filtered_data
    
    # Supported coverages mapped to ACORD forms
    SUPPORTED_COVERAGES = {
        "COMMERCIAL_GENERAL_LIABILITY": {"forms": ["ACORD_125", "ACORD_126"], "supported": True},
        "COMMERCIAL_PROPERTY": {"forms": ["ACORD_125", "ACORD_140"], "supported": True},
        "WORKERS_COMPENSATION": {"forms": ["ACORD_125", "ACORD_130"], "supported": True},
        "BUSINESS_AUTO": {"forms": ["ACORD_125", "ACORD_127"], "supported": True},
        "UMBRELLA": {"forms": ["ACORD_125"], "supported": True},
        "BUSINESS_OWNERS": {"forms": ["ACORD_125"], "supported": True},
        "LIQUOR_LIABILITY": {"forms": ["ACORD_125", "ACORD_126"], "supported": True},  # Uses GL section
        "MOTOR_CARRIER": {"forms": ["ACORD_125", "ACORD_127"], "supported": True},  # Uses auto section
        "TRUCKERS": {"forms": ["ACORD_125", "ACORD_127"], "supported": True},  # Uses auto section
        "CYBER_AND_PRIVACY": {"forms": ["ACORD_125"], "supported": True},
        "GARAGE_AND_DEALERS": {"forms": ["ACORD_125"], "supported": True},
        "PROFESSIONAL_LIABILITY": {"forms": ["ACORD_125"], "supported": True},
    }
    
    # Coverage name aliases for normalization
    # NOTE: Order matters for fuzzy matching! More specific aliases should come BEFORE generic ones.
    COVERAGE_ALIASES = {
        # Auto liability aliases (MUST come before generic "LIABILITY" to match correctly)
        "COMMERCIAL AUTO LIABILITY": "BUSINESS_AUTO",
        "AUTO LIABILITY": "BUSINESS_AUTO",
        "BUSINESS AUTO LIABILITY": "BUSINESS_AUTO",
        "COMMERCIAL AUTO": "BUSINESS_AUTO",
        "BUSINESS AUTO": "BUSINESS_AUTO",
        "AUTO": "BUSINESS_AUTO",
        "VEHICLE": "BUSINESS_AUTO",
        # GL aliases
        "GL": "COMMERCIAL_GENERAL_LIABILITY",
        "GENERAL LIABILITY": "COMMERCIAL_GENERAL_LIABILITY",
        "GENERAL_LIABILITY": "COMMERCIAL_GENERAL_LIABILITY",
        "CGL": "COMMERCIAL_GENERAL_LIABILITY",
        "LIABILITY": "COMMERCIAL_GENERAL_LIABILITY",  # Generic - must come after specific liability types
        # Property aliases
        "PROPERTY": "COMMERCIAL_PROPERTY",
        "COMMERCIAL PROPERTY": "COMMERCIAL_PROPERTY",
        "BPP": "COMMERCIAL_PROPERTY",
        "BUILDING": "COMMERCIAL_PROPERTY",
        # WC aliases
        "WC": "WORKERS_COMPENSATION",
        "WORKERS COMP": "WORKERS_COMPENSATION",
        "WORKERS' COMPENSATION": "WORKERS_COMPENSATION",
        "WORKCOMP": "WORKERS_COMPENSATION",
        # Other aliases
        "UMBRELLA": "UMBRELLA",
        "EXCESS": "UMBRELLA",
        "BOP": "BUSINESS_OWNERS",
        "LIQUOR": "LIQUOR_LIABILITY",
        "CYBER": "CYBER_AND_PRIVACY",
        "E&O": "PROFESSIONAL_LIABILITY",
        "PROFESSIONAL": "PROFESSIONAL_LIABILITY",
        "TRUCKING": "TRUCKERS",
        "MOTOR CARRIER": "MOTOR_CARRIER",
    }
    
    def _normalize_coverage(self, coverage_str: str) -> Optional[str]:
        """
        Normalize a coverage string to a standard coverage code.
        
        Args:
            coverage_str: Raw coverage string from extraction
            
        Returns:
            Normalized coverage code or None if not recognized
        """
        if not coverage_str:
            return None
            
        coverage_upper = str(coverage_str).upper().strip()
        
        # Direct match
        if coverage_upper in self.SUPPORTED_COVERAGES:
            return coverage_upper
        
        # Check aliases
        if coverage_upper in self.COVERAGE_ALIASES:
            return self.COVERAGE_ALIASES[coverage_upper]
        
        # Fuzzy match - check if any alias is contained in the string
        for alias, normalized in self.COVERAGE_ALIASES.items():
            if alias in coverage_upper:
                return normalized
        
        return None
    
    def detect_coverages_from_extraction(self, extracted_data: Dict[str, Any]) -> List[str]:
        """
        Detect which coverage types were found in the extraction using TWO-TIER approach.
        
        TIER 1 (Primary): Check for explicit coverage_requested field
        TIER 2 (Fallback): Infer from lines_of_business and business context
        
        Args:
            extracted_data: The extracted data from Phase 1
            
        Returns:
            Dict with detected coverages, detection method, and supported status
        """
        detected = []
        detection_method = "NONE"
        unsupported = []
        
        # =====================================================================
        # TIER 1: Check for EXPLICIT coverage requests
        # =====================================================================
        coverage_requested = extracted_data.get("coverage_requested", {})
        if isinstance(coverage_requested, dict):
            source = coverage_requested.get("source", "").upper()
            requested_values = coverage_requested.get("value", [])
            
            if source == "EXPLICIT" and isinstance(requested_values, list) and len(requested_values) > 0:
                logger.info(f"TIER 1: Found explicit coverage requests: {requested_values}")
                detection_method = "EXPLICIT"
                
                for cov in requested_values:
                    normalized = self._normalize_coverage(cov)
                    if normalized and normalized not in detected:
                        # Check if supported
                        if self.SUPPORTED_COVERAGES.get(normalized, {}).get("supported", False):
                            detected.append(normalized)
                        else:
                            unsupported.append(normalized)
                            logger.warning(f"Coverage '{normalized}' requested but not yet supported")
        
        # =====================================================================
        # TIER 2: If no explicit coverages, INFER from lines_of_business
        # =====================================================================
        if not detected:
            logger.info("TIER 2: No explicit coverage found, inferring from lines_of_business")
            detection_method = "INFERRED"
            
            lines_of_business = extracted_data.get("lines_of_business", {})
            if isinstance(lines_of_business, dict):
                lob_value = lines_of_business.get("value", [])
                if isinstance(lob_value, list):
                    for lob in lob_value:
                        normalized = self._normalize_coverage(lob)
                        if normalized and normalized not in detected:
                            if self.SUPPORTED_COVERAGES.get(normalized, {}).get("supported", False):
                                detected.append(normalized)
                            else:
                                if normalized not in unsupported:
                                    unsupported.append(normalized)
            
            # Also check nature of business for hints if still nothing detected
            if not detected:
                nature = extracted_data.get("nature_of_business", {})
                if isinstance(nature, dict):
                    desc = nature.get("description_of_primary_operations", {})
                    if isinstance(desc, dict):
                        desc = desc.get("value", "")
                    if desc:
                        desc_lower = str(desc).lower()
                        # Infer coverages from business description
                        if any(term in desc_lower for term in ["employee", "payroll", "workers comp", "construction", "contractor"]):
                            if "WORKERS_COMPENSATION" not in detected:
                                detected.append("WORKERS_COMPENSATION")
                        if any(term in desc_lower for term in ["restaurant", "food", "liquor", "bar", "alcohol"]):
                            if "COMMERCIAL_GENERAL_LIABILITY" not in detected:
                                detected.append("COMMERCIAL_GENERAL_LIABILITY")
                            if "liquor" in desc_lower or "bar" in desc_lower or "alcohol" in desc_lower:
                                if "LIQUOR_LIABILITY" not in detected:
                                    detected.append("LIQUOR_LIABILITY")
                        if any(term in desc_lower for term in ["trucking", "freight", "hauling", "transportation"]):
                            if "TRUCKERS" not in detected:
                                detected.append("TRUCKERS")
        
        # Log results
        logger.info(f"Coverage detection complete:")
        logger.info(f"  - Method: {detection_method}")
        logger.info(f"  - Detected (supported): {detected}")
        if unsupported:
            logger.info(f"  - Detected (NOT supported): {unsupported}")
        
        # Store detection metadata in extracted_data for later use
        extracted_data["_coverage_detection"] = {
            "method": detection_method,
            "supported_coverages": detected,
            "unsupported_coverages": unsupported,
        }
        
        return detected

    def extract_acord126_data(
        self,
        extracted_text: str,
        base_extracted_data: Dict[str, Any],
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Extract ACORD 126 (General Liability) specific data.
        Phase 2 extraction for GL coverage.
        
        Args:
            extracted_text: Raw text from documents
            base_extracted_data: Data already extracted in Phase 1
            confidence_threshold: Minimum confidence score
            
        Returns:
            GL-specific extracted data
        """
        if not self.client:
            raise HTTPException(status_code=503, detail="OpenAI service not available")
        
        try:
            prompt = self._create_acord126_extraction_prompt(extracted_text, base_extracted_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance data extraction specialist focusing on Commercial General Liability (CGL) coverage. Extract GL-specific data for ACORD 126 forms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            logger.info("Successfully extracted ACORD 126 (GL) specific data")
            return extracted_data
            
        except Exception as e:
            logger.error(f"ACORD 126 extraction failed: {str(e)}")
            return {}

    def _create_acord126_extraction_prompt(self, text: str, base_data: Dict[str, Any]) -> str:
        """Create extraction prompt for ACORD 126 GL-specific fields"""
        # Use larger text limit for multi-document submissions (GPT-4-turbo supports 128K tokens)
        text_limit = 50000
        return f"""
Extract ACORD 126 Commercial General Liability specific data from the following document text.

IMPORTANT: This submission may contain MULTIPLE DOCUMENTS separated by "--- DOCUMENT SEPARATOR ---".
- SEARCH ALL DOCUMENTS for GL-specific information
- Look for liability limits, class codes, schedule of hazards across all documents

Document Text:
{text[:text_limit]}

Base data already extracted (for context):
- Business Name: {self._get_nested_value(base_data, 'first_named_insured.name')}
- Business Description: {self._get_nested_value(base_data, 'nature_of_business.description_of_primary_operations')}

Please extract GL-specific information and return as JSON:

{{
    "general_liability": {{
        "coverage_type": {{"value": "OCCURRENCE or CLAIMS_MADE or null", "confidence": 0.0-1.0}},
        "retroactive_date": {{"value": "YYYY-MM-DD or null (for claims-made)", "confidence": 0.0-1.0}},
        
        "limits": {{
            "general_aggregate": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "products_completed_ops_aggregate": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "personal_advertising_injury": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "each_occurrence": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "damage_to_rented_premises": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "medical_expense": {{"value": "amount or null", "confidence": 0.0-1.0}}
        }},
        
        "schedule_of_harzards": {{
            "value": [
                {{
                    "location_number": "1",
                    "class_code": "GL class code or null",
                    "classification_description": "description",
                    "premium_basis": "AREA, GROSS_SALES, PAYROLL, UNITS, or OTHER",
                    "exposure": "exposure amount (sq ft, sales, payroll, units)",
                    "rate": "rate per $1000 or null",
                    "estimated_premium": "premium amount or null"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "deductibles": {{
            "_note": "Only extract if Status of Transaction = RENEWAL",
            "property_damage": {{
                "amount": {{"value": "deductible amount in $ or null", "confidence": 0.0-1.0}},
                "type": {{"value": "PER_CLAIM or PER_OCCURRENCE or null", "confidence": 0.0-1.0}}
            }},
            "bodily_injury": {{
                "amount": {{"value": "deductible amount in $ or null", "confidence": 0.0-1.0}},
                "type": {{"value": "PER_CLAIM or PER_OCCURRENCE or null", "confidence": 0.0-1.0}}
            }}
        }},
        
        "employment_liability": {{
            "deductible_per_claim": {{"value": "deductible amount in $ or null", "confidence": 0.0-1.0}},
            "number_of_employees": {{"value": "number or null", "confidence": 0.0-1.0}},
            "employees_covered_by_benefits_plan": {{"value": "number or null", "confidence": 0.0-1.0}},
            "retroactive_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}}
        }}
    }}
}}

INSTRUCTIONS:
1. Focus only on General Liability specific information
2. For limits, extract the numeric value only (no $ or commas)
3. Common GL class codes include 41665 (Offices), 10073 (Artisan Contractors), etc.
4. Premium basis: AREA=sq ft, GROSS_SALES=revenue, PAYROLL=wages, UNITS=other
5. Return null for fields not found, not empty strings
6. Return valid JSON only
7. Deductibles: Only extract if Status of Transaction = RENEWAL. Include Property Damage and Bodily Injury deductibles with their type (Per Claim or Per Occurrence)
"""

    def extract_acord130_data(
        self,
        extracted_text: str,
        base_extracted_data: Dict[str, Any],
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Extract ACORD 130 (Workers Compensation) specific data.
        Phase 2 extraction for WC coverage.
        
        Args:
            extracted_text: Raw text from documents
            base_extracted_data: Data already extracted in Phase 1
            confidence_threshold: Minimum confidence score
            
        Returns:
            WC-specific extracted data
        """
        if not self.client:
            raise HTTPException(status_code=503, detail="OpenAI service not available")
        
        try:
            prompt = self._create_acord130_extraction_prompt(extracted_text, base_extracted_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance data extraction specialist focusing on Workers Compensation coverage. Extract WC-specific data for ACORD 130 forms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            logger.info("Successfully extracted ACORD 130 (WC) specific data")
            return extracted_data
            
        except Exception as e:
            logger.error(f"ACORD 130 extraction failed: {str(e)}")
            return {}

    def _create_acord130_extraction_prompt(self, text: str, base_data: Dict[str, Any]) -> str:
        """Create extraction prompt for ACORD 130 WC-specific fields"""
        # Use larger text limit for multi-document submissions (GPT-4-turbo supports 128K tokens)
        text_limit = 50000
        return f"""
Extract ACORD 130 Workers Compensation specific data from the following document text.

IMPORTANT: This submission may contain MULTIPLE DOCUMENTS separated by "--- DOCUMENT SEPARATOR ---".
- SEARCH ALL DOCUMENTS for Workers Compensation information
- Look for payroll data, class codes, experience mod, employee counts across all documents

Document Text:
{text[:text_limit]}

Base data already extracted (for context):
- Business Name: {self._get_nested_value(base_data, 'first_named_insured.name')}
- FEIN: {self._get_nested_value(base_data, 'first_named_insured.fein_or_ssn')}
- Business Description: {self._get_nested_value(base_data, 'nature_of_business.description_of_primary_operations')}

Please extract Workers Compensation specific information and return as JSON:

{{
    "workers_compensation": {{
        "experience_mod": {{
            "mod_rate": {{"value": "experience mod rate (e.g., 1.00, 0.85, 1.15) or null", "confidence": 0.0-1.0}},
            "effective_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
            "expiration_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
            "bureau": {{"value": "NCCI or state bureau name or null", "confidence": 0.0-1.0}},
            "risk_id": {{"value": "experience rating ID or null", "confidence": 0.0-1.0}},
            "interstate_rating": {{"value": "true/false", "confidence": 0.0-1.0}}
        }},
        
        "states": {{
            "value": [
                {{
                    "state": "2-letter state code",
                    "is_monopolistic": "true/false (OH, WA, WY, ND are monopolistic)",
                    "total_payroll": "total payroll for state or null",
                    "estimated_premium": "premium for state or null"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "classifications": {{
            "value": [
                {{
                    "state": "2-letter state code",
                    "class_code": "NCCI class code (4 digits)",
                    "classification_description": "job classification description",
                    "number_of_employees": "count or null",
                    "annual_remuneration": "annual payroll for this class",
                    "rate": "rate per $100 of payroll or null",
                    "estimated_premium": "premium or null"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "owners_officers": {{
            "value": [
                {{
                    "name": "owner/officer name",
                    "title": "title (Owner, President, etc.)",
                    "ownership_percentage": "percentage or null",
                    "duties": "duties description or null",
                    "annual_remuneration": "salary/compensation or null",
                    "inclusion_status": "INCLUDED or EXCLUDED",
                    "class_code": "class code if included or null"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "subcontractors": {{
            "uses_subcontractors": {{"value": "true/false", "confidence": 0.0-1.0}},
            "annual_subcontractor_cost": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "requires_coi_from_subs": {{"value": "true/false", "confidence": 0.0-1.0}}
        }},
        
        "employee_counts": {{
            "total_employees": {{"value": "count or null", "confidence": 0.0-1.0}},
            "full_time": {{"value": "count or null", "confidence": 0.0-1.0}},
            "part_time": {{"value": "count or null", "confidence": 0.0-1.0}},
            "seasonal": {{"value": "count or null", "confidence": 0.0-1.0}}
        }},
        
        "total_annual_payroll": {{"value": "total payroll amount or null", "confidence": 0.0-1.0}},
        
        "safety_programs": {{
            "has_safety_program": {{"value": "true/false", "confidence": 0.0-1.0}},
            "has_drug_testing": {{"value": "true/false", "confidence": 0.0-1.0}},
            "has_return_to_work": {{"value": "true/false", "confidence": 0.0-1.0}}
        }},
        
        "claims_history": {{
            "has_claims_past_5_years": {{"value": "true/false", "confidence": 0.0-1.0}},
            "total_claims_count": {{"value": "count or null", "confidence": 0.0-1.0}},
            "total_incurred": {{"value": "amount or null", "confidence": 0.0-1.0}}
        }},
        
        "premium_summary": {{
            "estimated_annual_premium": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "deposit_premium": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "minimum_premium": {{"value": "amount or null", "confidence": 0.0-1.0}}
        }}
    }}
}}

INSTRUCTIONS:
1. Focus only on Workers Compensation specific information
2. Common WC class codes: 8810 (Clerical), 5403 (Carpentry), 8742 (Sales), 7380 (Drivers)
3. Experience mod rates typically range from 0.70 to 1.50 (1.00 is neutral)
4. Monopolistic states: OH, WA, WY, ND (state-run WC programs)
5. Extract payroll by classification if breakdown is available
6. Return null for fields not found
7. Return valid JSON only
"""

    def extract_acord140_data(
        self,
        extracted_text: str,
        base_extracted_data: Dict[str, Any],
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Extract ACORD 140 (Property) specific data.
        Phase 2 extraction for Property coverage.
        
        Args:
            extracted_text: Raw text from documents
            base_extracted_data: Data already extracted in Phase 1
            confidence_threshold: Minimum confidence score
            
        Returns:
            Property-specific extracted data
        """
        if not self.client:
            raise HTTPException(status_code=503, detail="OpenAI service not available")
        
        try:
            prompt = self._create_acord140_extraction_prompt(extracted_text, base_extracted_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance data extraction specialist focusing on Commercial Property coverage. Extract property-specific data for ACORD 140 forms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            logger.info("Successfully extracted ACORD 140 (Property) specific data")
            return extracted_data
            
        except Exception as e:
            logger.error(f"ACORD 140 extraction failed: {str(e)}")
            return {}

    def _create_acord140_extraction_prompt(self, text: str, base_data: Dict[str, Any]) -> str:
        """Create extraction prompt for ACORD 140 Property-specific fields"""
        # Get premises info from base data
        premises_info = base_data.get("premises", {})
        if isinstance(premises_info, dict):
            premises_info = premises_info.get("value", [])
        
        # Use larger text limit for multi-document submissions (GPT-4-turbo supports 128K tokens)
        text_limit = 50000
        return f"""
Extract ACORD 140 Commercial Property specific data from the following document text.

IMPORTANT: This submission may contain MULTIPLE DOCUMENTS separated by "--- DOCUMENT SEPARATOR ---".
- SEARCH ALL DOCUMENTS for Property information
- Look for building details, property values, construction types across all documents

Document Text:
{text[:text_limit]}

Base data already extracted (for context):
- Business Name: {self._get_nested_value(base_data, 'first_named_insured.name')}
- Known Premises: {json.dumps(premises_info)[:500] if premises_info else 'None'}

Please extract Property-specific information and return as JSON:

{{
    "property": {{
        "buildings": {{
            "value": [
                {{
                    "location_number": 1,
                    "building_number": 1,
                    "street_address": "address or null",
                    "city": "city or null",
                    "state": "2-letter state code or null",
                    "zip_code": "ZIP or null",
                    "construction_type": "FRAME, JOISTED_MASONRY, NON_COMBUSTIBLE, MASONRY_NON_COMBUSTIBLE, MODIFIED_FIRE_RESISTIVE, FIRE_RESISTIVE or null",
                    "roof_type": "BUILT_UP, COMPOSITION, METAL, SHINGLE, TILE, SLATE, WOOD or null",
                    "year_built": "year or null",
                    "number_of_stories": "count or null",
                    "total_area_sq_ft": "square footage or null",
                    "has_sprinklers": "true/false",
                    "sprinkler_coverage_percent": "percentage or null",
                    "has_fire_alarm": "true/false",
                    "has_burglar_alarm": "true/false",
                    "fire_protection_class": "1-10 or null",
                    "occupancy_type": "OWNER_OCCUPIED, TENANT_OCCUPIED, VACANT or null",
                    "occupancy_description": "how building is used"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "coverages": {{
            "value": [
                {{
                    "location_number": 1,
                    "building_number": 1,
                    "building_limit": "building value or null",
                    "building_valuation": "REPLACEMENT_COST, ACTUAL_CASH_VALUE, AGREED_VALUE or null",
                    "building_coinsurance": "percentage (80, 90, 100) or null",
                    "bpp_limit": "business personal property value or null",
                    "bpp_valuation": "REPLACEMENT_COST, ACTUAL_CASH_VALUE or null",
                    "business_income_limit": "BI limit or null",
                    "extra_expense_limit": "EE limit or null",
                    "cause_of_loss": "BASIC, BROAD, SPECIAL or null",
                    "deductible": "property deductible or null",
                    "wind_hail_deductible": "wind/hail deductible or null"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "total_insured_values": {{
            "total_building_value": {{"value": "sum of all building values or null", "confidence": 0.0-1.0}},
            "total_bpp_value": {{"value": "sum of all BPP values or null", "confidence": 0.0-1.0}},
            "total_tiv": {{"value": "total insured value or null", "confidence": 0.0-1.0}}
        }},
        
        "optional_coverages": {{
            "equipment_breakdown": {{"value": "true/false", "confidence": 0.0-1.0}},
            "earthquake": {{"value": "true/false", "confidence": 0.0-1.0}},
            "flood": {{"value": "true/false", "confidence": 0.0-1.0}},
            "ordinance_law": {{"value": "true/false", "confidence": 0.0-1.0}},
            "spoilage": {{"value": "true/false", "confidence": 0.0-1.0}}
        }},
        
        "scheduled_equipment": {{
            "value": [
                {{
                    "description": "equipment description",
                    "serial_number": "serial or null",
                    "value": "value or null"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "loss_history": {{
            "has_prior_losses": {{"value": "true/false", "confidence": 0.0-1.0}},
            "loss_count_5_years": {{"value": "count or null", "confidence": 0.0-1.0}},
            "total_loss_amount": {{"value": "amount or null", "confidence": 0.0-1.0}}
        }},
        
        "premium_summary": {{
            "building_premium": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "bpp_premium": {{"value": "amount or null", "confidence": 0.0-1.0}},
            "total_property_premium": {{"value": "amount or null", "confidence": 0.0-1.0}}
        }}
    }}
}}

INSTRUCTIONS:
1. Focus only on Commercial Property specific information
2. Construction types: FRAME (wood), JOISTED_MASONRY (brick/wood), NON_COMBUSTIBLE (metal), FIRE_RESISTIVE (concrete/steel)
3. Fire protection class: 1 is best, 10 is worst (rural areas)
4. Common coinsurance: 80%, 90%, 100%
5. Cause of loss: BASIC (fire, lightning), BROAD (adds more perils), SPECIAL (all-risk minus exclusions)
6. Extract building values and BPP (contents) values separately
7. Return null for fields not found
8. Return valid JSON only
"""

    def extract_acord127_data(
        self,
        extracted_text: str,
        base_extracted_data: Dict[str, Any],
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Extract ACORD 127 (Commercial Auto) specific data.
        Phase 2 extraction for Business Auto coverage.
        
        Args:
            extracted_text: Raw text from documents
            base_extracted_data: Data already extracted in Phase 1
            confidence_threshold: Minimum confidence score
            
        Returns:
            Auto-specific extracted data
        """
        if not self.client:
            raise HTTPException(status_code=503, detail="OpenAI service not available")
        
        try:
            prompt = self._create_acord127_extraction_prompt(extracted_text, base_extracted_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance data extraction specialist focusing on Commercial Auto coverage. Extract auto-specific data for ACORD 127 forms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            logger.info("Successfully extracted ACORD 127 (Commercial Auto) specific data")
            return extracted_data
            
        except Exception as e:
            logger.error(f"ACORD 127 extraction failed: {str(e)}")
            return {}

    def _create_acord127_extraction_prompt(self, text: str, base_data: Dict[str, Any]) -> str:
        """Create extraction prompt for ACORD 127 Commercial Auto specific fields"""
        # Use larger text limit for multi-document submissions (GPT-4-turbo supports 128K tokens)
        text_limit = 50000
        return f"""
Extract ACORD 127 Commercial Auto specific data from the following document text.

IMPORTANT: This submission may contain MULTIPLE DOCUMENTS separated by "--- DOCUMENT SEPARATOR ---".
- SEARCH ALL DOCUMENTS for vehicle and driver information
- Vehicle schedules may appear in a separate document - look for VINs, Year/Make/Model, vehicle lists
- Driver lists may appear in a separate document - look for driver names, license numbers, DOB

Document Text:
{text[:text_limit]}

Base data already extracted (for context):
- Business Name: {self._get_nested_value(base_data, 'first_named_insured.name')}
- FEIN: {self._get_nested_value(base_data, 'first_named_insured.fein_or_ssn')}
- Business Description: {self._get_nested_value(base_data, 'nature_of_business.description_of_primary_operations')}

Please extract Commercial Auto specific information and return as JSON:

{{
    "commercial_auto": {{
        "vehicle_schedule": {{
            "value": [
                {{
                    "vehicle_number": "sequence number",
                    "year": "vehicle year (YYYY)",
                    "make": "vehicle manufacturer",
                    "model": "vehicle model",
                    "vin": "17-character VIN",
                    "vehicle_type": "PRIVATE_PASSENGER, LIGHT_TRUCK, MEDIUM_TRUCK, HEAVY_TRUCK, TRACTOR, TRAILER, BUS, OTHER",
                    "body_type": "SEDAN, SUV, PICKUP, VAN, BOX_TRUCK, FLATBED, TANKER, REEFER, etc.",
                    "gvw_gwc": "gross vehicle weight or null",
                    "radius_of_operations": "LOCAL (0-50mi), INTERMEDIATE (51-200mi), LONG_HAUL (200+mi)",
                    "farthest_terminal": "farthest terminal location or null",
                    "cost_new": "original cost or null",
                    "actual_cash_value": "current value or null",
                    "stated_amount": "stated amount or null",
                    "primary_use": "SERVICE, COMMERCIAL, RETAIL, HAULING, DELIVERY, etc.",
                    "annual_mileage": "estimated annual miles or null"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "driver_schedule": {{
            "value": [
                {{
                    "driver_number": "sequence number",
                    "name": "driver full name",
                    "date_of_birth": "YYYY-MM-DD or null",
                    "license_number": "driver license number",
                    "license_state": "2-letter state code",
                    "license_class": "CDL_A, CDL_B, CDL_C, CLASS_D, etc.",
                    "endorsements": ["H (Hazmat), T (Double/Triple), P (Passenger), N (Tank), S (School Bus), X (Hazmat+Tank)]",
                    "date_hired": "YYYY-MM-DD or null",
                    "years_experience": "years of commercial driving or null",
                    "accidents_3_years": "count or 0",
                    "violations_3_years": "count or 0"
                }}
            ],
            "confidence": 0.0-1.0
        }},
        
        "garage_locations": {{
            "value": [
                {{
                    "location_number": 1,
                    "address": "full address",
                    "city": "city",
                    "state": "2-letter state code",
                    "zip": "zip code",
                    "vehicles_garaged": "number of vehicles at this location"
                }}
            ],
            "confidence": 0.0-1.0
        }}
    }}
}}

INSTRUCTIONS:
1. Focus only on Commercial Auto / Business Auto specific information
2. VINs are exactly 17 characters - validate if possible
3. CDL endorsements: H=Hazmat, T=Doubles/Triples, P=Passenger, N=Tank, S=School Bus, X=Hazmat+Tank
4. Vehicle types: PRIVATE_PASSENGER (cars, SUVs), LIGHT_TRUCK (<10,000 GVW), MEDIUM_TRUCK (10,001-26,000 GVW), HEAVY_TRUCK (>26,000 GVW)
5. Radius: LOCAL (0-50mi), INTERMEDIATE (51-200mi), LONG_HAUL (200+mi)
6. Extract ALL vehicles listed in any vehicle schedule
7. Extract ALL drivers listed in any driver schedule
8. DOT numbers are typically 5-8 digits
9. MC numbers are typically 6-7 digits prefixed with MC or MX
10. Return null for fields not found
11. Return valid JSON only
"""

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Helper to get nested dictionary values safely"""
        try:
            keys = path.split('.')
            value = data
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key, {})
                    if isinstance(value, dict) and 'value' in value:
                        value = value.get('value')
                else:
                    return None
            return value if value != {} else None
        except Exception:
            return None

    def generate_risk_narrative(self, extracted_data: Dict[str, Any]) -> str:
        """
        Generate a risk narrative based on extracted data
        
        Args:
            extracted_data: Structured data extracted from documents
            
        Returns:
            Generated risk narrative text
        """
        if not self.client:
            raise HTTPException(status_code=503, detail="OpenAI service not available")
        
        try:
            prompt = f"""
Based on the following insurance data, generate a professional risk narrative for a commercial insurance application:

{json.dumps(extracted_data, indent=2)}

Please generate a 2-3 paragraph risk narrative that:
1. Describes the business and its operations
2. Identifies key risk factors and exposures
3. Highlights any notable characteristics that underwriters should consider
4. Uses professional insurance terminology
5. Is suitable for inclusion in an ACORD 125 application

Return only the narrative text, no additional formatting or explanations.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance underwriter writing risk narratives for commercial insurance applications."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            narrative = response.choices[0].message.content.strip()
            logger.info("Successfully generated risk narrative")
            return narrative
            
        except Exception as e:
            logger.error(f"Failed to generate risk narrative: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate risk narrative: {str(e)}")


# Global OpenAI service instance
openai_service = OpenAIService()




