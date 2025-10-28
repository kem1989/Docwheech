"""
Enhanced ACORD 125 Commercial Insurance Application Schema
Updated to match database models with 30+ critical fields
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# Import enums from database models
from app.models.acord_125 import (
    BusinessStructureEnum,
    TransactionTypeEnum,
    LineOfBusinessEnum,
    InterestEnum,
    CarrierCategoryEnum,
)


class AgencySchema(BaseModel):
    """Agency information schema"""
    name: Optional[str] = Field(None, description="Agency name")
    code: Optional[str] = Field(None, description="Agency code")
    subcode: Optional[str] = Field(None, description="Agency subcode")
    agency_customer_id: Optional[str] = Field(None, description="Agency customer ID")
    address: Optional[str] = Field(None, description="Agency address")
    contact_name: Optional[str] = Field(None, description="Agency contact name")
    phone: Optional[str] = Field(None, description="Agency phone")
    fax: Optional[str] = Field(None, description="Agency fax")
    email: Optional[str] = Field(None, description="Agency email")


class TransactionStatusSchema(BaseModel):
    """Transaction status schema"""
    type: Optional[TransactionTypeEnum] = Field(None, description="Transaction type")
    bound_date: Optional[date] = Field(None, description="Bound date")
    bound_time: Optional[str] = Field(None, description="Bound time (HH:MM AM/PM)")


class PolicySchema(BaseModel):
    """Policy information schema"""
    proposed_effective_date: Optional[date] = Field(None, description="Proposed effective date")
    proposed_expiration_date: Optional[date] = Field(None, description="Proposed expiration date")
    billing_plan: Optional[str] = Field(None, description="Billing plan")
    payment_plan: Optional[str] = Field(None, description="Payment plan")
    audit: Optional[bool] = Field(False, description="Audit required")
    deposit_premium: Optional[Decimal] = Field(None, description="Deposit premium amount")
    minimum_premium: Optional[Decimal] = Field(None, description="Minimum premium amount")
    method_of_payment: Optional[str] = Field(None, description="Method of payment")


class LineOfBusinessSchema(BaseModel):
    """Line of business schema"""
    line: Optional[LineOfBusinessEnum] = Field(None, description="Line of business type")
    selected: Optional[bool] = Field(False, description="Whether this line is selected")
    premium: Optional[Decimal] = Field(None, description="Premium amount for this line")


class FirstNamedInsuredSchema(BaseModel):
    """First named insured schema"""
    name: Optional[str] = Field(None, description="Legal name of the insured")
    mailing_address: Optional[str] = Field(None, description="Mailing address")
    business_structure: Optional[BusinessStructureEnum] = Field(None, description="Business structure")
    number_of_members: Optional[int] = Field(None, description="Number of LLC members")
    number_of_managers: Optional[int] = Field(None, description="Number of LLC managers")
    naics_code: Optional[str] = Field(None, description="NAICS code")
    sic_code: Optional[str] = Field(None, description="SIC code")
    gl_code: Optional[str] = Field(None, description="General liability code")
    fein_or_ssn: Optional[str] = Field(None, description="FEIN or SSN")
    business_phone: Optional[str] = Field(None, description="Business phone number")
    website_address: Optional[str] = Field(None, description="Website address")


class ContactSchema(BaseModel):
    """Contact information schema"""
    contact_type: Optional[str] = Field(None, description="Type of contact")
    contact_name: Optional[str] = Field(None, description="Contact name")
    primary_email: Optional[str] = Field(None, description="Primary email address")
    secondary_email: Optional[str] = Field(None, description="Secondary email address")
    primary_phone: Optional[str] = Field(None, description="Primary phone number")
    primary_phone_type: Optional[str] = Field(None, description="Primary phone type (HOME, BUSINESS, CELL)")
    secondary_phone: Optional[str] = Field(None, description="Secondary phone number")
    secondary_phone_type: Optional[str] = Field(None, description="Secondary phone type")


class NatureOfBusinessSchema(BaseModel):
    """Nature of business schema"""
    date_business_started: Optional[date] = Field(None, description="Date business started")
    business_type: Optional[List[str]] = Field(None, description="List of business types")
    description_of_primary_operations: Optional[str] = Field(None, description="Description of primary operations")
    retail_stores_or_service_operations: Optional[bool] = Field(False, description="Has retail stores or service operations")
    retail_percent_of_total_sales: Optional[Decimal] = Field(None, description="Retail percentage of total sales")
    installation_service_repair_work: Optional[bool] = Field(False, description="Does installation/service/repair work")
    off_premises_installation_service_repair: Optional[bool] = Field(False, description="Off-premises installation/service/repair")
    description_of_operations_other_named_insureds: Optional[str] = Field(None, description="Description of operations for other named insureds")


class PremiseSchema(BaseModel):
    """Premises information schema"""
    location_number: Optional[int] = Field(None, description="Location number")
    building_number: Optional[int] = Field(None, description="Building number")
    street_address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    county: Optional[str] = Field(None, description="County")
    state: Optional[str] = Field(None, description="State abbreviation")
    zip: Optional[str] = Field(None, description="ZIP code")
    city_limits: Optional[bool] = Field(False, description="Within city limits")
    description_of_operations: Optional[str] = Field(None, description="Description of operations at this location")
    interest: Optional[InterestEnum] = Field(None, description="Property interest")
    owner_or_tenant_inside: Optional[bool] = Field(False, description="Owner or tenant inside")
    owner_or_tenant_outside: Optional[bool] = Field(False, description="Owner or tenant outside")
    number_full_time_employees: Optional[int] = Field(None, description="Number of full-time employees")
    number_part_time_employees: Optional[int] = Field(None, description="Number of part-time employees")
    annual_revenues: Optional[Decimal] = Field(None, description="Annual revenues")
    occupied_area_sq_ft: Optional[Decimal] = Field(None, description="Occupied area in square feet")
    total_building_area_sq_ft: Optional[Decimal] = Field(None, description="Total building area in square feet")
    open_to_public_area_sq_ft: Optional[Decimal] = Field(None, description="Open to public area in square feet")
    any_area_leased_to_others: Optional[bool] = Field(False, description="Any area leased to others")


class PriorCarrierSchema(BaseModel):
    """Prior carrier information schema"""
    category: Optional[CarrierCategoryEnum] = Field(None, description="Carrier category")
    carrier_name: Optional[str] = Field(None, description="Prior carrier name")
    policy_number: Optional[str] = Field(None, description="Policy number")
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiration_date: Optional[date] = Field(None, description="Expiration date")
    premium: Optional[Decimal] = Field(None, description="Premium amount")
    years_with_carrier: Optional[int] = Field(None, description="Years with carrier")


class LossSchema(BaseModel):
    """Individual loss schema"""
    date_of_loss: Optional[date] = Field(None, description="Date of loss")
    line_type: Optional[str] = Field(None, description="Line type")
    description_of_occurrence: Optional[str] = Field(None, description="Description of occurrence")
    amount_paid: Optional[Decimal] = Field(None, description="Amount paid")
    amount_reserved: Optional[Decimal] = Field(None, description="Amount reserved")
    claim_open: Optional[bool] = Field(False, description="Claim is open")
    subrogation: Optional[bool] = Field(False, description="Subrogation involved")


class LossHistorySchema(BaseModel):
    """Loss history schema"""
    has_losses: Optional[bool] = Field(False, description="Has losses")
    total_losses_amount: Optional[Decimal] = Field(None, description="Total losses amount")
    losses: Optional[List[LossSchema]] = Field(None, description="List of individual losses")


class SignatureSchema(BaseModel):
    """Signature schema"""
    signature_type: Optional[str] = Field(None, description="Type of signature (applicant, producer)")
    signature_data: Optional[str] = Field(None, description="Digital signature or image")
    signer_name: Optional[str] = Field(None, description="Signer name")
    signature_date: Optional[date] = Field(None, description="Signature date")
    state_producer_license_number: Optional[str] = Field(None, description="State producer license number")
    national_producer_number: Optional[str] = Field(None, description="National producer number")


class ACORD125Schema(BaseModel):
    """
    Enhanced ACORD 125 Commercial Insurance Application Schema
    Contains 30+ critical fields for comprehensive data extraction
    """
    
    # Agency Information
    agency: Optional[AgencySchema] = Field(None, description="Agency information")
    
    # Transaction Status
    transaction_status: Optional[TransactionStatusSchema] = Field(None, description="Transaction status")
    
    # Policy Information
    policy: Optional[PolicySchema] = Field(None, description="Policy information")
    
    # Lines of Business
    lines_of_business: Optional[List[LineOfBusinessSchema]] = Field(None, description="Lines of business")
    
    # First Named Insured
    first_named_insured: Optional[FirstNamedInsuredSchema] = Field(None, description="First named insured information")
    
    # Contact Information
    contacts: Optional[List[ContactSchema]] = Field(None, description="Contact information")
    
    # Nature of Business
    nature_of_business: Optional[NatureOfBusinessSchema] = Field(None, description="Nature of business")
    
    # Premises
    premises: Optional[List[PremiseSchema]] = Field(None, description="Premises information")
    
    # Prior Carriers
    prior_carriers: Optional[List[PriorCarrierSchema]] = Field(None, description="Prior carriers")
    
    # Loss History
    loss_history: Optional[LossHistorySchema] = Field(None, description="Loss history")
    
    # Signatures
    signatures: Optional[List[SignatureSchema]] = Field(None, description="Signatures")
    
    # Metadata
    extraction_timestamp: Optional[datetime] = Field(None, description="When data was extracted")
    extraction_confidence: Optional[float] = Field(None, description="Overall extraction confidence score")
    source_documents: Optional[List[str]] = Field(None, description="Source document identifiers")
    validation_status: Optional[str] = Field(None, description="Validation status (extracted, validated, etc.)")
    risk_narrative: Optional[str] = Field(None, description="AI-generated risk narrative for the business")
    
    @validator('state', 'agency_state', 'state_of_incorporation', check_fields=False)
    def validate_state(cls, v):
        """Validate state abbreviations"""
        if v and len(v) != 2:
            # Try to convert full state name to abbreviation
            state_map = {
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
                'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC'
            }
            return state_map.get(v.lower(), v)
        return v
    
    @validator('phone', 'business_phone', 'primary_phone', 'secondary_phone', check_fields=False)
    def validate_phone(cls, v):
        """Validate and format phone numbers"""
        if v:
            # Remove all non-digit characters
            digits = ''.join(filter(str.isdigit, v))
            if len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return v
    
    @validator('email', 'primary_email', 'secondary_email', check_fields=False)
    def validate_email(cls, v):
        """Validate email format"""
        if v and '@' not in v:
            return None
        return v
    
    def get_critical_fields_count(self) -> int:
        """Get count of populated critical fields"""
        critical_fields = [
            'agency.name', 'first_named_insured.name', 'first_named_insured.business_structure',
            'first_named_insured.naics_code', 'nature_of_business.description_of_primary_operations',
            'policy.proposed_effective_date', 'policy.proposed_expiration_date',
            'transaction_status.type', 'lines_of_business', 'premises'
        ]
        
        count = 0
        for field_path in critical_fields:
            if self._get_nested_field(field_path) is not None:
                count += 1
        
        return count
    
    def _get_nested_field(self, field_path: str) -> Any:
        """Get nested field value using dot notation"""
        try:
            obj = self
            for field in field_path.split('.'):
                obj = getattr(obj, field, None)
                if obj is None:
                    return None
            return obj
        except:
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary"""
        return self.dict(exclude_none=True)
    
    def get_completion_percentage(self) -> float:
        """Calculate completion percentage based on critical fields"""
        total_critical = 10  # Total number of critical field groups
        populated = self.get_critical_fields_count()
        return (populated / total_critical) * 100


def create_acord_schema_from_extraction(extracted_data: Dict[str, Any]) -> ACORD125Schema:
    """
    Create ACORD125Schema from extracted data
    
    Args:
        extracted_data: Raw extracted data from AI/Textract
        
    Returns:
        ACORD125Schema instance
    """
    try:
        # Map extracted data to schema fields
        schema_data = {}
        
        # Agency information
        if 'agency' in extracted_data:
            schema_data['agency'] = AgencySchema(**extracted_data['agency'])
        
        # Transaction status
        if 'transaction_status' in extracted_data:
            schema_data['transaction_status'] = TransactionStatusSchema(**extracted_data['transaction_status'])
        
        # Policy information
        if 'policy' in extracted_data:
            schema_data['policy'] = PolicySchema(**extracted_data['policy'])
        
        # Lines of business
        if 'lines_of_business' in extracted_data:
            schema_data['lines_of_business'] = [
                LineOfBusinessSchema(**lob) for lob in extracted_data['lines_of_business']
            ]
        
        # First named insured
        if 'first_named_insured' in extracted_data:
            schema_data['first_named_insured'] = FirstNamedInsuredSchema(**extracted_data['first_named_insured'])
        
        # Contacts
        if 'contacts' in extracted_data:
            schema_data['contacts'] = [
                ContactSchema(**contact) for contact in extracted_data['contacts']
            ]
        
        # Nature of business
        if 'nature_of_business' in extracted_data:
            schema_data['nature_of_business'] = NatureOfBusinessSchema(**extracted_data['nature_of_business'])
        
        # Premises
        if 'premises' in extracted_data:
            schema_data['premises'] = [
                PremiseSchema(**premise) for premise in extracted_data['premises']
            ]
        
        # Prior carriers
        if 'prior_carriers' in extracted_data:
            schema_data['prior_carriers'] = [
                PriorCarrierSchema(**carrier) for carrier in extracted_data['prior_carriers']
            ]
        
        # Loss history
        if 'loss_history' in extracted_data:
            loss_data = extracted_data['loss_history']
            if 'losses' in loss_data:
                loss_data['losses'] = [LossSchema(**loss) for loss in loss_data['losses']]
            schema_data['loss_history'] = LossHistorySchema(**loss_data)
        
        # Signatures
        if 'signatures' in extracted_data:
            schema_data['signatures'] = [
                SignatureSchema(**sig) for sig in extracted_data['signatures']
            ]
        
        # Metadata
        schema_data['extraction_timestamp'] = datetime.now()
        schema_data['extraction_confidence'] = extracted_data.get('confidence', 0.0)
        schema_data['source_documents'] = extracted_data.get('source_documents', [])
        
        return ACORD125Schema(**schema_data)
        
    except Exception as e:
        # Return empty schema if parsing fails
        return ACORD125Schema()