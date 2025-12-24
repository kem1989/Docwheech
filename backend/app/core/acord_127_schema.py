"""
ACORD 127 Commercial Auto Section Schema

This module defines the schema for ACORD 127 form data,
matching the fields extracted by the commercial_auto prompt.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import date


class VehicleScheduleItem(BaseModel):
    """Vehicle schedule entry"""
    vehicle_number: Optional[str] = None
    year: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    vin: Optional[str] = None
    vehicle_type: Optional[str] = None
    body_type: Optional[str] = None
    gvw_gwc: Optional[str] = None
    radius_of_operations: Optional[str] = None
    farthest_terminal: Optional[str] = None
    cost_new: Optional[str] = None
    actual_cash_value: Optional[str] = None
    stated_amount: Optional[str] = None
    primary_use: Optional[str] = None
    annual_mileage: Optional[str] = None


class DriverScheduleItem(BaseModel):
    """Driver schedule entry"""
    driver_number: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    license_number: Optional[str] = None
    license_state: Optional[str] = None
    license_class: Optional[str] = None
    endorsements: Optional[List[str]] = None
    date_hired: Optional[str] = None
    years_experience: Optional[str] = None
    accidents_3_years: Optional[str] = None
    violations_3_years: Optional[str] = None


class GarageLocationItem(BaseModel):
    """Garage location entry"""
    location_number: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    vehicles_garaged: Optional[str] = None


class ACORD127Schema(BaseModel):
    """
    ACORD 127 Commercial Auto Section Schema
    
    Contains vehicle schedule, driver schedule, and garage locations.
    """
    # Header fields (from ACORD 125)
    named_insured: Optional[str] = None
    policy_number: Optional[str] = None
    effective_date: Optional[str] = None
    producer_name: Optional[str] = None
    
    # Vehicle Schedule
    vehicle_schedule: List[VehicleScheduleItem] = Field(default_factory=list)
    
    # Driver Schedule
    driver_schedule: List[DriverScheduleItem] = Field(default_factory=list)
    
    # Garage Locations
    garage_locations: List[GarageLocationItem] = Field(default_factory=list)
    
    # Remarks
    remarks: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary for PDF filling"""
        result = {}
        
        # Header
        if self.named_insured:
            result["named_insured"] = self.named_insured
        if self.policy_number:
            result["policy_number"] = self.policy_number
        if self.effective_date:
            result["effective_date"] = self.effective_date
        if self.producer_name:
            result["producer_name"] = self.producer_name
        
        # Vehicle Schedule - flatten for PDF field mapping
        for idx, vehicle in enumerate(self.vehicle_schedule):
            prefix = f"vehicle_schedule[{idx}]"
            if vehicle.year:
                result[f"{prefix}.year"] = vehicle.year
            if vehicle.make:
                result[f"{prefix}.make"] = vehicle.make
            if vehicle.model:
                result[f"{prefix}.model"] = vehicle.model
            if vehicle.vin:
                result[f"{prefix}.vin"] = vehicle.vin
            if vehicle.body_type:
                result[f"{prefix}.body_type"] = vehicle.body_type
            if vehicle.gvw_gwc:
                result[f"{prefix}.gvw"] = vehicle.gvw_gwc
            if vehicle.cost_new:
                result[f"{prefix}.cost_new"] = vehicle.cost_new
            if vehicle.radius_of_operations:
                result[f"{prefix}.radius"] = vehicle.radius_of_operations
            if vehicle.stated_amount:
                result[f"{prefix}.stated_amount"] = vehicle.stated_amount
        
        # Driver Schedule - flatten for PDF field mapping
        for idx, driver in enumerate(self.driver_schedule):
            prefix = f"driver_schedule[{idx}]"
            
            # Handle name splitting
            if driver.name:
                name_parts = driver.name.split()
                if len(name_parts) >= 2:
                    result[f"{prefix}.first_name"] = name_parts[0]
                    result[f"{prefix}.last_name"] = " ".join(name_parts[1:])
                else:
                    result[f"{prefix}.first_name"] = driver.name
            
            if driver.first_name:
                result[f"{prefix}.first_name"] = driver.first_name
            if driver.last_name:
                result[f"{prefix}.last_name"] = driver.last_name
            if driver.date_of_birth:
                result[f"{prefix}.date_of_birth"] = driver.date_of_birth
            if driver.license_number:
                result[f"{prefix}.license_number"] = driver.license_number
            if driver.license_state:
                result[f"{prefix}.license_state"] = driver.license_state
            if driver.years_experience:
                result[f"{prefix}.years_experience"] = driver.years_experience
            if driver.date_hired:
                result[f"{prefix}.date_hired"] = driver.date_hired
        
        # Garage Locations - map to first vehicle's garage address
        for idx, garage in enumerate(self.garage_locations):
            prefix = f"vehicle_schedule[{idx}]"
            if garage.address:
                result[f"{prefix}.garage_address"] = garage.address
            if garage.city:
                result[f"{prefix}.garage_city"] = garage.city
            if garage.state:
                result[f"{prefix}.garage_state"] = garage.state
            if garage.zip:
                result[f"{prefix}.garage_zip"] = garage.zip
        
        if self.remarks:
            result["remarks"] = self.remarks
        
        return result


def create_acord127_from_extraction(extracted_data: Dict[str, Any]) -> ACORD127Schema:
    """
    Create ACORD127Schema from extracted data.
    
    Args:
        extracted_data: Raw extracted data containing commercial_auto section
        
    Returns:
        ACORD127Schema populated with extracted data
    """
    schema = ACORD127Schema()
    
    # Get header info from first_named_insured
    first_named = extracted_data.get("first_named_insured", {})
    if isinstance(first_named, dict):
        name_data = first_named.get("name", {})
        if isinstance(name_data, dict):
            schema.named_insured = name_data.get("value")
        elif isinstance(name_data, str):
            schema.named_insured = name_data
    
    # Get policy info
    policy = extracted_data.get("policy", {})
    if isinstance(policy, dict):
        eff_date = policy.get("proposed_effective_date", {})
        if isinstance(eff_date, dict):
            schema.effective_date = eff_date.get("value")
        elif isinstance(eff_date, str):
            schema.effective_date = eff_date
    
    # Get agency info
    agency = extracted_data.get("agency", {})
    if isinstance(agency, dict):
        agency_name = agency.get("name", {})
        if isinstance(agency_name, dict):
            schema.producer_name = agency_name.get("value")
        elif isinstance(agency_name, str):
            schema.producer_name = agency_name
    
    # Get commercial_auto data
    commercial_auto = extracted_data.get("commercial_auto", {})
    if not isinstance(commercial_auto, dict):
        commercial_auto = {}
    
    # Parse vehicle_schedule
    vehicle_schedule_data = commercial_auto.get("vehicle_schedule", {})
    if isinstance(vehicle_schedule_data, dict):
        vehicles = vehicle_schedule_data.get("value", [])
    elif isinstance(vehicle_schedule_data, list):
        vehicles = vehicle_schedule_data
    else:
        vehicles = []
    
    for v in vehicles:
        if isinstance(v, dict):
            vehicle = VehicleScheduleItem(
                vehicle_number=_get_value(v.get("vehicle_number")),
                year=_get_value(v.get("year")),
                make=_get_value(v.get("make")),
                model=_get_value(v.get("model")),
                vin=_get_value(v.get("vin")),
                vehicle_type=_get_value(v.get("vehicle_type")),
                body_type=_get_value(v.get("body_type")),
                gvw_gwc=_get_value(v.get("gvw_gwc")),
                radius_of_operations=_get_value(v.get("radius_of_operations")),
                farthest_terminal=_get_value(v.get("farthest_terminal")),
                cost_new=_get_value(v.get("cost_new")),
                actual_cash_value=_get_value(v.get("actual_cash_value")),
                stated_amount=_get_value(v.get("stated_amount")),
                primary_use=_get_value(v.get("primary_use")),
                annual_mileage=_get_value(v.get("annual_mileage")),
            )
            schema.vehicle_schedule.append(vehicle)
    
    # Parse driver_schedule
    driver_schedule_data = commercial_auto.get("driver_schedule", {})
    if isinstance(driver_schedule_data, dict):
        drivers = driver_schedule_data.get("value", [])
    elif isinstance(driver_schedule_data, list):
        drivers = driver_schedule_data
    else:
        drivers = []
    
    for d in drivers:
        if isinstance(d, dict):
            driver = DriverScheduleItem(
                driver_number=_get_value(d.get("driver_number")),
                name=_get_value(d.get("name")),
                date_of_birth=_get_value(d.get("date_of_birth")),
                license_number=_get_value(d.get("license_number")),
                license_state=_get_value(d.get("license_state")),
                license_class=_get_value(d.get("license_class")),
                endorsements=d.get("endorsements") if isinstance(d.get("endorsements"), list) else None,
                date_hired=_get_value(d.get("date_hired")),
                years_experience=_get_value(d.get("years_experience")),
                accidents_3_years=_get_value(d.get("accidents_3_years")),
                violations_3_years=_get_value(d.get("violations_3_years")),
            )
            schema.driver_schedule.append(driver)
    
    # Parse garage_locations
    garage_data = commercial_auto.get("garage_locations", {})
    if isinstance(garage_data, dict):
        garages = garage_data.get("value", [])
    elif isinstance(garage_data, list):
        garages = garage_data
    else:
        garages = []
    
    for g in garages:
        if isinstance(g, dict):
            garage = GarageLocationItem(
                location_number=g.get("location_number"),
                address=_get_value(g.get("address")),
                city=_get_value(g.get("city")),
                state=_get_value(g.get("state")),
                zip=_get_value(g.get("zip")),
                vehicles_garaged=_get_value(g.get("vehicles_garaged")),
            )
            schema.garage_locations.append(garage)
    
    return schema


def _get_value(data: Any) -> Optional[str]:
    """Extract value from data that might be wrapped in {value, confidence} format"""
    if data is None:
        return None
    if isinstance(data, dict):
        return str(data.get("value")) if data.get("value") is not None else None
    return str(data) if data else None


