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
        return f"""
Extract ACORD 125 Commercial Insurance Application data from the following {file_type.upper()} document text and return it in the specified JSON format.

Document Text:
{text[:6000]}

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
        "type": {{"value": "QUOTE, RENEWAL, ISSUE_POLICY, BOUND, CANCEL, CHANGE or null", "confidence": 0.0-1.0}},
        "bound_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
        "bound_time": {{"value": "HH:MM AM/PM or null", "confidence": 0.0-1.0}}
    }},
    "policy": {{
        "proposed_effective_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
        "proposed_expiration_date": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
        "billing_plan": {{"value": "billing plan or null", "confidence": 0.0-1.0}},
        "deposit_premium": {{"value": "deposit premium amount or null", "confidence": 0.0-1.0}},
        "minimum_premium": {{"value": "minimum premium or null", "confidence": 0.0-1.0}}
    }},
    "lines_of_business": {{
        "value": [
            "ONLY select from these ENUM values based on the business operations described in the document: COMMERCIAL_GENERAL_LIABILITY, COMMERCIAL_PROPERTY, BUSINESS_AUTO, UMBRELLA, BUSINESS_OWNERS, GARAGE_AND_DEALERS, CRIME, BOILER_AND_MACHINERY, COMMERCIAL_INLAND_MARINE, CYBER_AND_PRIVACY, FIDUCIARY_LIABILITY, LIQUOR_LIABILITY, MOTOR_CARRIER, TRUCKERS, YACHT. If none apply, return an empty array []"
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
    "contacts": {{
        "value": ["list of contact objects with type, name, email, phone or null"],
        "confidence": 0.0-1.0
    }},
    "nature_of_business": {{
        "date_business_started": {{"value": "YYYY-MM-DD or null", "confidence": 0.0-1.0}},
        "business_type": {{"value": ["array of business type strings like 'manufacturing', 'retail', 'wholesale', etc. or empty array []"], "confidence": 0.0-1.0}},
        "description_of_primary_operations": {{"value": "primary operations description or null", "confidence": 0.0-1.0}},
        "retail_stores_or_service_operations": {{"value": "true/false or null", "confidence": 0.0-1.0}}
    }},
    "premises": {{
        "value": ["list of premise objects with street address, city, state, zip, operations description, employees, revenues, square footage or null"],
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
1. Only extract information that is clearly present in the text
2. Use null for missing information, not empty strings or empty arrays
3. For dates, use YYYY-MM-DD format
4. For numbers, extract only numeric values (no currency symbols)
5. For business structure, use ENUM values: INDIVIDUAL, LLC, CORPORATION, PARTNERSHIP, JOINT_VENTURE, NOT_FOR_PROFIT_ORG, SUBCHAPTER_S_CORPORATION, TRUST
6. For transaction type, use: QUOTE, RENEWAL, ISSUE_POLICY, BOUND, CANCEL, CHANGE
7. Lines of Business rules:
   - STRICTLY select ONLY from: COMMERCIAL_GENERAL_LIABILITY, COMMERCIAL_PROPERTY, BUSINESS_AUTO, UMBRELLA, BUSINESS_OWNERS, GARAGE_AND_DEALERS, CRIME, BOILER_AND_MACHINERY, COMMERCIAL_INLAND_MARINE, CYBER_AND_PRIVACY, FIDUCIARY_LIABILITY, LIQUOR_LIABILITY, MOTOR_CARRIER, TRUCKERS, YACHT
   - DO NOT include Workers Compensation under any circumstance
   - Derive primarily from explicit request phrases (e.g., "Need quotes on", "Coverage requested", "Apply for", "Requested coverages")
   - Use prior carriers ONLY as supporting context; do not add coverages unless they are also requested in the document
8. For business_type, extract as ARRAY of strings (e.g., ["manufacturing", "wholesale", "retail"]). Derive from industry descriptions or explicit business classifications in the text.
9. Assign confidence scores based on how clearly information is stated
10. If information is ambiguous or unclear, assign lower confidence (<0.7)
11. Return only valid JSON format
12. For arrays (lines_of_business, contacts, premises, business_type, etc.), return empty array [] if no data found
13. NAICS codes must be 6 digits
14. Phone numbers should be in format: (XXX) XXX-XXXX
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




