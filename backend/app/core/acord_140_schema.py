"""
ACORD 140 - Property Section Schema

This form captures detailed Commercial Property information including:
- Building information and construction details
- Coverage amounts and valuation
- Loss history
- Optional coverages
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from enum import Enum


class ConstructionTypeEnum(str, Enum):
    """Building construction types"""
    FRAME = "FRAME"
    JOISTED_MASONRY = "JOISTED_MASONRY"
    NON_COMBUSTIBLE = "NON_COMBUSTIBLE"
    MASONRY_NON_COMBUSTIBLE = "MASONRY_NON_COMBUSTIBLE"
    MODIFIED_FIRE_RESISTIVE = "MODIFIED_FIRE_RESISTIVE"
    FIRE_RESISTIVE = "FIRE_RESISTIVE"


class RoofTypeEnum(str, Enum):
    """Roof types"""
    BUILT_UP = "BUILT_UP"
    COMPOSITION = "COMPOSITION"
    METAL = "METAL"
    SHINGLE = "SHINGLE"
    TILE = "TILE"
    SLATE = "SLATE"
    WOOD = "WOOD"
    OTHER = "OTHER"


class OccupancyTypeEnum(str, Enum):
    """Occupancy types"""
    OWNER_OCCUPIED = "OWNER_OCCUPIED"
    TENANT_OCCUPIED = "TENANT_OCCUPIED"
    VACANT = "VACANT"
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"


class ValuationTypeEnum(str, Enum):
    """Valuation methods"""
    REPLACEMENT_COST = "REPLACEMENT_COST"
    ACTUAL_CASH_VALUE = "ACTUAL_CASH_VALUE"
    AGREED_VALUE = "AGREED_VALUE"
    FUNCTIONAL_REPLACEMENT = "FUNCTIONAL_REPLACEMENT"


class CauseOfLossEnum(str, Enum):
    """Cause of loss coverage types"""
    BASIC = "BASIC"
    BROAD = "BROAD"
    SPECIAL = "SPECIAL"


class BuildingInfoSchema(BaseModel):
    """Building information"""
    location_number: Optional[int] = Field(None, description="Location number")
    building_number: Optional[int] = Field(None, description="Building number")
    
    # Address
    street_address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    county: Optional[str] = Field(None, description="County")
    
    # Construction details
    construction_type: Optional[ConstructionTypeEnum] = Field(None, description="Construction type")
    roof_type: Optional[RoofTypeEnum] = Field(None, description="Roof type")
    roof_year: Optional[int] = Field(None, description="Year roof installed/updated")
    year_built: Optional[int] = Field(None, description="Year built")
    number_of_stories: Optional[int] = Field(None, description="Number of stories")
    total_area_sq_ft: Optional[Decimal] = Field(None, description="Total area in sq ft")
    occupied_area_sq_ft: Optional[Decimal] = Field(None, description="Area occupied by insured")
    
    # Building features
    has_sprinklers: Optional[bool] = Field(False, description="Has automatic sprinklers")
    sprinkler_coverage_percent: Optional[int] = Field(None, description="% of building with sprinklers")
    has_fire_alarm: Optional[bool] = Field(False, description="Has fire alarm system")
    alarm_type: Optional[str] = Field(None, description="Type of alarm (local, central, etc.)")
    has_burglar_alarm: Optional[bool] = Field(False, description="Has burglar alarm")
    distance_to_fire_station: Optional[Decimal] = Field(None, description="Miles to fire station")
    distance_to_fire_hydrant: Optional[Decimal] = Field(None, description="Feet to fire hydrant")
    fire_protection_class: Optional[str] = Field(None, description="Fire protection class")
    
    # Occupancy
    occupancy_type: Optional[OccupancyTypeEnum] = Field(None, description="Occupancy type")
    occupancy_description: Optional[str] = Field(None, description="Detailed occupancy description")
    percent_occupied: Optional[int] = Field(None, description="Percentage occupied")
    
    # Updates
    wiring_update_year: Optional[int] = Field(None, description="Year electrical updated")
    plumbing_update_year: Optional[int] = Field(None, description="Year plumbing updated")
    heating_update_year: Optional[int] = Field(None, description="Year heating updated")


class PropertyCoverageSchema(BaseModel):
    """Property coverage amounts"""
    location_number: Optional[int] = Field(None, description="Location number")
    building_number: Optional[int] = Field(None, description="Building number")
    
    # Coverage amounts
    building_limit: Optional[Decimal] = Field(None, description="Building coverage limit")
    building_valuation: Optional[ValuationTypeEnum] = Field(None, description="Building valuation type")
    building_coinsurance: Optional[int] = Field(None, description="Building coinsurance %")
    
    bpp_limit: Optional[Decimal] = Field(None, description="Business Personal Property limit")
    bpp_valuation: Optional[ValuationTypeEnum] = Field(None, description="BPP valuation type")
    bpp_coinsurance: Optional[int] = Field(None, description="BPP coinsurance %")
    
    business_income_limit: Optional[Decimal] = Field(None, description="Business Income limit")
    extra_expense_limit: Optional[Decimal] = Field(None, description="Extra Expense limit")
    
    # Cause of loss
    cause_of_loss: Optional[CauseOfLossEnum] = Field(None, description="Cause of loss form")
    
    # Deductibles
    deductible: Optional[Decimal] = Field(None, description="Property deductible")
    wind_hail_deductible: Optional[Decimal] = Field(None, description="Wind/Hail deductible")
    wind_hail_deductible_percent: Optional[int] = Field(None, description="Wind/Hail deductible %")
    
    # Premium
    building_premium: Optional[Decimal] = Field(None, description="Building premium")
    bpp_premium: Optional[Decimal] = Field(None, description="BPP premium")
    bi_ee_premium: Optional[Decimal] = Field(None, description="Business Income/Extra Expense premium")


class OptionalCoverageSchema(BaseModel):
    """Optional property coverages"""
    coverage_name: Optional[str] = Field(None, description="Coverage name")
    limit: Optional[Decimal] = Field(None, description="Limit")
    deductible: Optional[Decimal] = Field(None, description="Deductible")
    premium: Optional[Decimal] = Field(None, description="Premium")
    description: Optional[str] = Field(None, description="Description")


class ScheduledPropertySchema(BaseModel):
    """Scheduled/inland marine property"""
    item_description: Optional[str] = Field(None, description="Item description")
    serial_number: Optional[str] = Field(None, description="Serial number")
    value: Optional[Decimal] = Field(None, description="Value")
    location: Optional[str] = Field(None, description="Location")


class ACORD140Schema(BaseModel):
    """
    ACORD 140 - Property Section Schema
    """
    # Header information
    named_insured: Optional[str] = Field(None, description="Named insured")
    policy_number: Optional[str] = Field(None, description="Policy number")
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiration_date: Optional[date] = Field(None, description="Expiration date")
    
    # Buildings
    buildings: Optional[List[BuildingInfoSchema]] = Field(
        None, description="Building information"
    )
    
    # Coverages
    coverages: Optional[List[PropertyCoverageSchema]] = Field(
        None, description="Property coverages"
    )
    
    # Optional coverages
    optional_coverages: Optional[List[OptionalCoverageSchema]] = Field(
        None, description="Optional coverages"
    )
    
    # Common optional coverages (quick flags)
    equipment_breakdown: Optional[bool] = Field(False, description="Equipment breakdown coverage")
    earthquake: Optional[bool] = Field(False, description="Earthquake coverage")
    flood: Optional[bool] = Field(False, description="Flood coverage")
    ordinance_law: Optional[bool] = Field(False, description="Ordinance or law coverage")
    spoilage: Optional[bool] = Field(False, description="Spoilage coverage")
    
    # Inland Marine / Scheduled Property
    scheduled_property: Optional[List[ScheduledPropertySchema]] = Field(
        None, description="Scheduled property items"
    )
    
    # Premium summary
    total_building_premium: Optional[Decimal] = Field(None, description="Total building premium")
    total_bpp_premium: Optional[Decimal] = Field(None, description="Total BPP premium")
    total_bi_ee_premium: Optional[Decimal] = Field(None, description="Total BI/EE premium")
    total_optional_premium: Optional[Decimal] = Field(None, description="Total optional coverage premium")
    total_property_premium: Optional[Decimal] = Field(None, description="Total property premium")
    
    # Loss history
    prior_losses: Optional[bool] = Field(False, description="Any prior property losses")
    loss_count_5_years: Optional[int] = Field(None, description="Number of losses in 5 years")
    total_loss_amount: Optional[Decimal] = Field(None, description="Total loss amount")
    
    # Additional remarks
    additional_remarks: Optional[str] = Field(None, description="Additional remarks")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary"""
        return self.dict(exclude_none=True)
    
    def get_total_insured_values(self) -> Dict[str, Decimal]:
        """Calculate total insured values"""
        total_building = Decimal("0")
        total_bpp = Decimal("0")
        
        if self.coverages:
            for cov in self.coverages:
                if cov.building_limit:
                    total_building += cov.building_limit
                if cov.bpp_limit:
                    total_bpp += cov.bpp_limit
        
        return {
            "total_building": total_building,
            "total_bpp": total_bpp,
            "total_tiv": total_building + total_bpp,
        }


def create_acord140_from_extraction(extracted_data: Dict[str, Any]) -> ACORD140Schema:
    """
    Create ACORD140Schema from extracted data
    
    Args:
        extracted_data: Raw extracted data
        
    Returns:
        ACORD140Schema instance
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
            
            exp_date = policy.get("proposed_expiration_date")
            if isinstance(exp_date, dict):
                exp_date = exp_date.get("value")
            schema_data["expiration_date"] = exp_date
        
        # Map premises to buildings
        premises = extracted_data.get("premises", [])
        if premises:
            if isinstance(premises, dict) and "value" in premises:
                premises = premises.get("value", [])
            
            buildings = []
            for idx, premise in enumerate(premises):
                if not isinstance(premise, dict):
                    continue
                
                def unwrap(val):
                    if isinstance(val, dict) and "value" in val:
                        return val.get("value")
                    return val
                
                building = BuildingInfoSchema(
                    location_number=idx + 1,
                    building_number=1,
                    street_address=unwrap(premise.get("street_address")),
                    city=unwrap(premise.get("city")),
                    state=unwrap(premise.get("state")),
                    zip_code=unwrap(premise.get("zip")),
                    total_area_sq_ft=unwrap(premise.get("total_building_area_sq_ft")),
                    occupied_area_sq_ft=unwrap(premise.get("occupied_area_sq_ft")),
                    occupancy_description=unwrap(premise.get("description_of_operations")),
                )
                buildings.append(building)
            
            if buildings:
                schema_data["buildings"] = buildings
        
        # Map property-specific data if available
        property_data = extracted_data.get("property", {})
        if property_data:
            # Buildings from property data
            prop_buildings = property_data.get("buildings", [])
            if prop_buildings:
                schema_data["buildings"] = [
                    BuildingInfoSchema(**b) for b in prop_buildings
                ]
            
            # Coverages
            coverages = property_data.get("coverages", [])
            if coverages:
                schema_data["coverages"] = [
                    PropertyCoverageSchema(**c) for c in coverages
                ]
        
        return ACORD140Schema(**schema_data)
        
    except Exception as e:
        return ACORD140Schema()

















