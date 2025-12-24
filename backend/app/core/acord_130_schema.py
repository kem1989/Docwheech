"""
ACORD 130 - Workers Compensation Application Schema

This form captures detailed Workers Compensation information including:
- Payroll by classification
- Experience modification
- State-specific information
- Employee details
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from enum import Enum


class OwnerOfficerInclusionEnum(str, Enum):
    """Owner/Officer inclusion status"""
    INCLUDED = "INCLUDED"
    EXCLUDED = "EXCLUDED"


class WCClassificationSchema(BaseModel):
    """Workers Compensation classification information"""
    state: Optional[str] = Field(None, description="State code (2 letters)")
    location_number: Optional[int] = Field(None, description="Location number")
    class_code: Optional[str] = Field(None, description="NCCI class code")
    classification_description: Optional[str] = Field(None, description="Classification description")
    number_of_employees: Optional[int] = Field(None, description="Number of employees in this class")
    full_time_employees: Optional[int] = Field(None, description="Full-time employees")
    part_time_employees: Optional[int] = Field(None, description="Part-time employees")
    annual_remuneration: Optional[Decimal] = Field(None, description="Annual payroll/remuneration")
    rate: Optional[Decimal] = Field(None, description="Rate per $100 of payroll")
    estimated_premium: Optional[Decimal] = Field(None, description="Estimated premium")


class OwnerOfficerSchema(BaseModel):
    """Owner/Officer information for WC"""
    name: Optional[str] = Field(None, description="Owner/Officer name")
    title: Optional[str] = Field(None, description="Title/Position")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    ownership_percentage: Optional[Decimal] = Field(None, description="Ownership percentage")
    duties: Optional[str] = Field(None, description="Duties description")
    annual_remuneration: Optional[Decimal] = Field(None, description="Annual remuneration")
    inclusion_status: Optional[OwnerOfficerInclusionEnum] = Field(
        None, description="Included or Excluded from coverage"
    )
    class_code: Optional[str] = Field(None, description="Class code if included")


class StateInfoSchema(BaseModel):
    """State-specific WC information"""
    state: Optional[str] = Field(None, description="State code")
    is_monopolistic: Optional[bool] = Field(False, description="Is monopolistic state")
    other_states_coverage: Optional[bool] = Field(False, description="Other states coverage applies")
    total_payroll: Optional[Decimal] = Field(None, description="Total payroll for state")
    estimated_premium: Optional[Decimal] = Field(None, description="Estimated premium for state")


class ExperienceModSchema(BaseModel):
    """Experience modification information"""
    mod_rate: Optional[Decimal] = Field(None, description="Experience mod rate (e.g., 1.00)")
    effective_date: Optional[date] = Field(None, description="Mod rate effective date")
    expiration_date: Optional[date] = Field(None, description="Mod rate expiration date")
    bureau: Optional[str] = Field(None, description="Rating bureau (NCCI, state bureau, etc.)")
    risk_id: Optional[str] = Field(None, description="Risk ID/Experience rating ID")
    interstate_rating: Optional[bool] = Field(False, description="Interstate experience rating")


class PriorPolicySchema(BaseModel):
    """Prior WC policy information"""
    carrier_name: Optional[str] = Field(None, description="Prior carrier name")
    policy_number: Optional[str] = Field(None, description="Policy number")
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiration_date: Optional[date] = Field(None, description="Expiration date")
    premium: Optional[Decimal] = Field(None, description="Premium")
    mod_rate: Optional[Decimal] = Field(None, description="Experience mod rate")


class ACORD130Schema(BaseModel):
    """
    ACORD 130 - Workers Compensation Application Schema
    """
    # Header information
    named_insured: Optional[str] = Field(None, description="Named insured")
    fein: Optional[str] = Field(None, description="Federal Employer ID Number")
    policy_number: Optional[str] = Field(None, description="Policy number")
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiration_date: Optional[date] = Field(None, description="Expiration date")
    
    # Business information
    legal_entity: Optional[str] = Field(None, description="Legal entity type")
    date_business_started: Optional[date] = Field(None, description="Date business started")
    nature_of_business: Optional[str] = Field(None, description="Nature of business description")
    sic_code: Optional[str] = Field(None, description="SIC code")
    naics_code: Optional[str] = Field(None, description="NAICS code")
    
    # Contact information
    contact_name: Optional[str] = Field(None, description="Contact name")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    contact_email: Optional[str] = Field(None, description="Contact email")
    
    # Experience modification
    experience_mod: Optional[ExperienceModSchema] = Field(
        None, description="Experience modification info"
    )
    
    # State information
    states: Optional[List[StateInfoSchema]] = Field(
        None, description="State-specific information"
    )
    
    # Classifications/Payroll
    classifications: Optional[List[WCClassificationSchema]] = Field(
        None, description="WC classifications with payroll"
    )
    
    # Owner/Officer information
    owners_officers: Optional[List[OwnerOfficerSchema]] = Field(
        None, description="Owner/Officer information"
    )
    
    # Subcontractor information
    uses_subcontractors: Optional[bool] = Field(False, description="Uses subcontractors")
    subcontractor_cost: Optional[Decimal] = Field(None, description="Annual subcontractor cost")
    requires_coi_from_subs: Optional[bool] = Field(False, description="Requires COI from subs")
    
    # Employee counts
    total_employees: Optional[int] = Field(None, description="Total employee count")
    full_time_employees: Optional[int] = Field(None, description="Full-time employees")
    part_time_employees: Optional[int] = Field(None, description="Part-time employees")
    seasonal_employees: Optional[int] = Field(None, description="Seasonal employees")
    
    # Premium summary
    total_estimated_annual_premium: Optional[Decimal] = Field(
        None, description="Total estimated annual premium"
    )
    deposit_premium: Optional[Decimal] = Field(None, description="Deposit premium")
    minimum_premium: Optional[Decimal] = Field(None, description="Minimum premium")
    
    # Prior coverage
    prior_policies: Optional[List[PriorPolicySchema]] = Field(
        None, description="Prior WC policies"
    )
    
    # Claims history
    claims_past_5_years: Optional[bool] = Field(False, description="Claims in past 5 years")
    total_claims_count: Optional[int] = Field(None, description="Total claims count")
    total_claims_amount: Optional[Decimal] = Field(None, description="Total claims amount paid")
    
    # Additional information
    safety_program: Optional[bool] = Field(False, description="Has formal safety program")
    drug_testing: Optional[bool] = Field(False, description="Has drug testing program")
    return_to_work_program: Optional[bool] = Field(False, description="Has return to work program")
    
    # Remarks
    additional_remarks: Optional[str] = Field(None, description="Additional remarks")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary"""
        return self.dict(exclude_none=True)
    
    def get_total_payroll(self) -> Decimal:
        """Calculate total payroll from all classifications"""
        if not self.classifications:
            return Decimal("0")
        return sum(
            c.annual_remuneration or Decimal("0") 
            for c in self.classifications
        )


def create_acord130_from_extraction(extracted_data: Dict[str, Any]) -> ACORD130Schema:
    """
    Create ACORD130Schema from extracted data
    
    Args:
        extracted_data: Raw extracted data
        
    Returns:
        ACORD130Schema instance
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
            
            fein = first_named_insured.get("fein_or_ssn")
            if isinstance(fein, dict):
                fein = fein.get("value")
            schema_data["fein"] = fein
        
        policy = extracted_data.get("policy", {})
        if isinstance(policy, dict):
            eff_date = policy.get("proposed_effective_date")
            if isinstance(eff_date, dict):
                eff_date = eff_date.get("value")
            schema_data["effective_date"] = eff_date
            
            exp_date = policy.get("proposed_expiration_date")
            if isinstance(exp_date, dict):
                exp_date = exp_date.get("value")
            schema_data["expiration_date"] = exp_date
        
        nature_of_business = extracted_data.get("nature_of_business", {})
        if isinstance(nature_of_business, dict):
            desc = nature_of_business.get("description_of_primary_operations")
            if isinstance(desc, dict):
                desc = desc.get("value")
            schema_data["nature_of_business"] = desc
        
        # Map WC-specific data if available
        wc_data = extracted_data.get("workers_compensation", {})
        if wc_data:
            # Experience mod
            exp_mod = wc_data.get("experience_mod", {})
            if exp_mod:
                schema_data["experience_mod"] = ExperienceModSchema(**exp_mod)
            
            # Classifications
            classifications = wc_data.get("classifications", [])
            if classifications:
                schema_data["classifications"] = [
                    WCClassificationSchema(**c) for c in classifications
                ]
            
            # Owners/Officers
            owners = wc_data.get("owners_officers", [])
            if owners:
                schema_data["owners_officers"] = [
                    OwnerOfficerSchema(**o) for o in owners
                ]
        
        # Get employee counts from premises if available
        premises = extracted_data.get("premises", [])
        if premises and isinstance(premises, list) and len(premises) > 0:
            first_premise = premises[0]
            if isinstance(first_premise, dict):
                ft = first_premise.get("number_full_time_employees")
                if isinstance(ft, dict):
                    ft = ft.get("value")
                pt = first_premise.get("number_part_time_employees")
                if isinstance(pt, dict):
                    pt = pt.get("value")
                
                if ft:
                    schema_data["full_time_employees"] = int(ft) if ft else None
                if pt:
                    schema_data["part_time_employees"] = int(pt) if pt else None
                if ft and pt:
                    schema_data["total_employees"] = (int(ft) if ft else 0) + (int(pt) if pt else 0)
        
        return ACORD130Schema(**schema_data)
        
    except Exception as e:
        return ACORD130Schema()

















