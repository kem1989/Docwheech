"""
ACORD 126 - Commercial General Liability Section Schema

This form captures detailed General Liability information including:
- Classification and premium basis
- Coverage limits
- Products/Completed Operations
- Additional coverages and endorsements
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from enum import Enum


class OccurrenceClaimsMadeEnum(str, Enum):
    """Occurrence vs Claims Made"""
    OCCURRENCE = "OCCURRENCE"
    CLAIMS_MADE = "CLAIMS_MADE"


class PremiumBasisEnum(str, Enum):
    """Premium basis types"""
    AREA = "AREA"
    GROSS_SALES = "GROSS_SALES"
    PAYROLL = "PAYROLL"
    UNITS = "UNITS"
    OTHER = "OTHER"


class GLClassificationSchema(BaseModel):
    """GL Classification/Hazard information"""
    location_number: Optional[int] = Field(None, description="Location number")
    building_number: Optional[int] = Field(None, description="Building number")
    classification_description: Optional[str] = Field(None, description="Classification description")
    class_code: Optional[str] = Field(None, description="GL class code")
    premium_basis: Optional[PremiumBasisEnum] = Field(None, description="Premium basis type")
    exposure: Optional[Decimal] = Field(None, description="Exposure amount")
    rate: Optional[Decimal] = Field(None, description="Rate")
    premium: Optional[Decimal] = Field(None, description="Premium amount")
    
    # Products/Completed Operations
    pco_class_code: Optional[str] = Field(None, description="Products/CO class code")
    pco_exposure: Optional[Decimal] = Field(None, description="Products/CO exposure")
    pco_rate: Optional[Decimal] = Field(None, description="Products/CO rate")
    pco_premium: Optional[Decimal] = Field(None, description="Products/CO premium")


class GLLimitsSchema(BaseModel):
    """General Liability limits"""
    general_aggregate: Optional[Decimal] = Field(None, description="General Aggregate limit")
    products_co_aggregate: Optional[Decimal] = Field(None, description="Products/Completed Ops Aggregate")
    personal_advertising_injury: Optional[Decimal] = Field(None, description="Personal & Advertising Injury limit")
    each_occurrence: Optional[Decimal] = Field(None, description="Each Occurrence limit")
    damage_to_rented_premises: Optional[Decimal] = Field(None, description="Damage to Rented Premises limit")
    medical_expense: Optional[Decimal] = Field(None, description="Medical Expense limit")
    employee_benefits_aggregate: Optional[Decimal] = Field(None, description="Employee Benefits Aggregate")
    employee_benefits_each_employee: Optional[Decimal] = Field(None, description="Employee Benefits Each Employee")


class ClaimsMadeInfoSchema(BaseModel):
    """Claims-made specific information"""
    retroactive_date: Optional[date] = Field(None, description="Retroactive date")
    entry_date: Optional[date] = Field(None, description="Entry date")


class AdditionalCoverageSchema(BaseModel):
    """Additional coverage information"""
    coverage_description: Optional[str] = Field(None, description="Coverage description")
    limit: Optional[Decimal] = Field(None, description="Limit")
    deductible: Optional[Decimal] = Field(None, description="Deductible")
    premium: Optional[Decimal] = Field(None, description="Premium")


class ACORD126Schema(BaseModel):
    """
    ACORD 126 - Commercial General Liability Section Schema
    """
    # Header information (usually copied from ACORD 125)
    named_insured: Optional[str] = Field(None, description="Named insured")
    policy_number: Optional[str] = Field(None, description="Policy number")
    effective_date: Optional[date] = Field(None, description="Effective date")
    
    # Coverage type
    occurrence_claims_made: Optional[OccurrenceClaimsMadeEnum] = Field(
        None, description="Occurrence or Claims-Made"
    )
    
    # Claims-made info (if applicable)
    claims_made_info: Optional[ClaimsMadeInfoSchema] = Field(
        None, description="Claims-made specific info"
    )
    
    # Limits
    limits: Optional[GLLimitsSchema] = Field(None, description="GL limits")
    
    # Classifications
    classifications: Optional[List[GLClassificationSchema]] = Field(
        None, description="GL classifications and hazards"
    )
    
    # Deductibles
    deductible_type: Optional[str] = Field(None, description="Deductible type (Per Claim/Per Occurrence)")
    deductible_amount: Optional[Decimal] = Field(None, description="Deductible amount")
    deductible_applies_to: Optional[str] = Field(None, description="What deductible applies to")
    
    # Additional coverages
    additional_coverages: Optional[List[AdditionalCoverageSchema]] = Field(
        None, description="Additional coverages"
    )
    
    # Premium summary
    premises_operations_premium: Optional[Decimal] = Field(None, description="Premises/Operations premium")
    products_co_premium: Optional[Decimal] = Field(None, description="Products/CO premium")
    other_premium: Optional[Decimal] = Field(None, description="Other coverages premium")
    total_premium: Optional[Decimal] = Field(None, description="Total GL premium")
    
    # Endorsements and additional info
    endorsements: Optional[str] = Field(None, description="Endorsements description")
    additional_remarks: Optional[str] = Field(None, description="Additional remarks")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary"""
        return self.dict(exclude_none=True)


def create_acord126_from_extraction(extracted_data: Dict[str, Any]) -> ACORD126Schema:
    """
    Create ACORD126Schema from extracted data
    
    Args:
        extracted_data: Raw extracted data
        
    Returns:
        ACORD126Schema instance
    """
    try:
        schema_data = {}
        
        # Map common fields from ACORD 125 extraction
        first_named_insured = extracted_data.get("first_named_insured", {})
        if isinstance(first_named_insured, dict):
            name = first_named_insured.get("name")
            if isinstance(name, dict):
                name = name.get("value")
            schema_data["named_insured"] = name
        
        policy = extracted_data.get("policy", {})
        if isinstance(policy, dict):
            eff_date = policy.get("proposed_effective_date")
            if isinstance(eff_date, dict):
                eff_date = eff_date.get("value")
            schema_data["effective_date"] = eff_date
        
        # Map GL-specific data if available
        gl_data = extracted_data.get("general_liability", {})
        if gl_data:
            # Limits
            limits_data = gl_data.get("limits", {})
            if limits_data:
                schema_data["limits"] = GLLimitsSchema(**limits_data)
            
            # Classifications
            classifications = gl_data.get("classifications", [])
            if classifications:
                schema_data["classifications"] = [
                    GLClassificationSchema(**c) for c in classifications
                ]
        
        return ACORD126Schema(**schema_data)
        
    except Exception as e:
        return ACORD126Schema()

















