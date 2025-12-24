"""
Coverage Requirements Matrix for Context-Aware Gap Detection

This module defines what data and documents are required for each line of business.
The gap detection system uses this to check ONLY what's relevant for the specific
coverages a client is requesting.
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class RequirementSeverity(str, Enum):
    """Severity level for requirements"""
    CRITICAL = "critical"      # Cannot submit without this
    IMPORTANT = "important"    # Strongly recommended
    RECOMMENDED = "recommended"  # Nice to have


class RequirementType(str, Enum):
    """Type of requirement"""
    DATA_FIELD = "data_field"      # A specific field in the extracted data
    DOCUMENT = "document"          # A document type that should be uploaded
    CONDITIONAL = "conditional"    # Depends on other factors


# =============================================================================
# COVERAGE REQUIREMENTS MATRIX
# =============================================================================

COVERAGE_REQUIREMENTS: Dict[str, Dict[str, Any]] = {
    
    # =========================================================================
    # COMMERCIAL GENERAL LIABILITY
    # =========================================================================
    "COMMERCIAL_GENERAL_LIABILITY": {
        "display_name": "Commercial General Liability",
        "short_name": "GL",
        "required_documents": [
            {
                "id": "loss_runs_5_year",
                "name": "Loss Runs (5-Year)",
                "description": "5-year claims history from current/prior carriers",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "current_policy_dec",
                "name": "Current Policy Declarations Page",
                "description": "Declarations page from current GL policy",
                "severity": RequirementSeverity.IMPORTANT,
            },
        ],
        "required_data": [
            # =====================================================================
            # ACORD 126 GL-SPECIFIC FIELDS
            # =====================================================================
            {
                "id": "gl_coverage_type",
                "field_path": "general_liability.coverage_type.value",
                "label": "GL Coverage Type (Occurrence/Claims-Made)",
                "section": "General Liability",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "gl_retroactive_date",
                "field_path": "general_liability.retroactive_date.value",
                "label": "Retroactive Date (for Claims-Made)",
                "section": "General Liability",
                "severity": RequirementSeverity.IMPORTANT,
            },
            # GL Limits
            {
                "id": "gl_general_aggregate",
                "field_path": "general_liability.limits.general_aggregate.value",
                "label": "General Aggregate Limit",
                "section": "General Liability - Limits",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "gl_products_completed_ops_aggregate",
                "field_path": "general_liability.limits.products_completed_ops_aggregate.value",
                "label": "Products/Completed Ops Aggregate Limit",
                "section": "General Liability - Limits",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "gl_personal_advertising_injury",
                "field_path": "general_liability.limits.personal_advertising_injury.value",
                "label": "Personal & Advertising Injury Limit",
                "section": "General Liability - Limits",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "gl_each_occurrence",
                "field_path": "general_liability.limits.each_occurrence.value",
                "label": "Each Occurrence Limit",
                "section": "General Liability - Limits",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "gl_damage_to_rented_premises",
                "field_path": "general_liability.limits.damage_to_rented_premises.value",
                "label": "Damage to Rented Premises Limit",
                "section": "General Liability - Limits",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "gl_medical_expense",
                "field_path": "general_liability.limits.medical_expense.value",
                "label": "Medical Expense Limit",
                "section": "General Liability - Limits",
                "severity": RequirementSeverity.IMPORTANT,
            },
            # Schedule of Hazards
            {
                "id": "gl_schedule_of_hazards",
                "field_path": "general_liability.schedule_of_harzards.value",
                "label": "Schedule of Hazards / Classifications",
                "section": "General Liability - Schedule of Hazards",
                "severity": RequirementSeverity.CRITICAL,
                "check_type": "array_not_empty",
            },
            # Employment Liability
            {
                "id": "gl_employment_deductible_per_claim",
                "field_path": "general_liability.employment_liability.deductible_per_claim.value",
                "label": "Employment Liability - Deductible Per Claim",
                "section": "General Liability - Employment Liability",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "gl_employment_number_of_employees",
                "field_path": "general_liability.employment_liability.number_of_employees.value",
                "label": "Employment Liability - Number of Employees",
                "section": "General Liability - Employment Liability",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "gl_employment_employees_covered",
                "field_path": "general_liability.employment_liability.employees_covered_by_benefits_plan.value",
                "label": "Employment Liability - Employees Covered by Benefits Plan",
                "section": "General Liability - Employment Liability",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "gl_employment_retroactive_date",
                "field_path": "general_liability.employment_liability.retroactive_date.value",
                "label": "Employment Liability - Retroactive Date",
                "section": "General Liability - Employment Liability",
                "severity": RequirementSeverity.IMPORTANT,
            },
        ],
        "conditional_requirements": [
            # GL Deductibles - Only for RENEWAL transactions
            {
                "condition": "transaction_status.type == 'RENEWAL'",
                "requires": [
                    {
                        "id": "gl_deductible_property_damage_amount",
                        "field_path": "general_liability.deductibles.property_damage.amount.value",
                        "label": "GL Deductible - Property Damage Amount",
                        "severity": RequirementSeverity.IMPORTANT,
                    },
                    {
                        "id": "gl_deductible_property_damage_type",
                        "field_path": "general_liability.deductibles.property_damage.type.value",
                        "label": "GL Deductible - Property Damage Type (Per Claim/Per Occurrence)",
                        "severity": RequirementSeverity.IMPORTANT,
                    },
                    {
                        "id": "gl_deductible_bodily_injury_amount",
                        "field_path": "general_liability.deductibles.bodily_injury.amount.value",
                        "label": "GL Deductible - Bodily Injury Amount",
                        "severity": RequirementSeverity.IMPORTANT,
                    },
                    {
                        "id": "gl_deductible_bodily_injury_type",
                        "field_path": "general_liability.deductibles.bodily_injury.type.value",
                        "label": "GL Deductible - Bodily Injury Type (Per Claim/Per Occurrence)",
                        "severity": RequirementSeverity.IMPORTANT,
                    },
                ],
            },
        ],
    },
    
    # =========================================================================
    # COMMERCIAL PROPERTY
    # =========================================================================
    "COMMERCIAL_PROPERTY": {
        "display_name": "Commercial Property",
        "short_name": "Property",
        "required_documents": [
            {
                "id": "property_schedule",
                "name": "Property Schedule / Statement of Values",
                "description": "List of all property with values, construction types, etc.",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "loss_runs_5_year",
                "name": "Loss Runs (5-Year)",
                "description": "5-year property claims history",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "premises_address",
                "field_path": "premises[0].street_address",
                "label": "Property Address",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "building_value",
                "field_path": "premises[0].building_value",
                "label": "Building Value / Replacement Cost",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "contents_value",
                "field_path": "premises[0].contents_value",
                "label": "Business Personal Property (Contents) Value",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "construction_type",
                "field_path": "premises[0].construction_type",
                "label": "Construction Type (Frame, Masonry, etc.)",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "year_built",
                "field_path": "premises[0].year_built",
                "label": "Year Built",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "square_footage",
                "field_path": "premises[0].total_building_area_sq_ft",
                "label": "Square Footage",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "occupancy",
                "field_path": "premises[0].interest",
                "label": "Interest (Owner/Tenant)",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [
            {
                "condition": "premises[0].year_built < 1990",
                "requires": [
                    {"id": "roof_update", "label": "Roof Update Date", "severity": RequirementSeverity.IMPORTANT},
                    {"id": "electrical_update", "label": "Electrical Update Date", "severity": RequirementSeverity.IMPORTANT},
                    {"id": "plumbing_update", "label": "Plumbing Update Date", "severity": RequirementSeverity.IMPORTANT},
                    {"id": "hvac_update", "label": "HVAC Update Date", "severity": RequirementSeverity.IMPORTANT},
                ],
            },
            {
                "condition": "premises[0].state in ['FL', 'TX', 'LA', 'SC', 'NC', 'GA']",
                "requires": [
                    {"id": "wind_mitigation", "label": "Wind Mitigation Form", "severity": RequirementSeverity.IMPORTANT},
                ],
            },
        ],
    },
    
    # =========================================================================
    # BUSINESS AUTO / COMMERCIAL AUTO
    # =========================================================================
    "BUSINESS_AUTO": {
        "display_name": "Commercial Auto",
        "short_name": "Auto",
        "required_documents": [
            {
                "id": "vehicle_schedule",
                "name": "Vehicle Schedule",
                "description": "List of all vehicles with Year/Make/Model/VIN",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "driver_list",
                "name": "Driver List",
                "description": "List of all drivers with DOB, license number, hire date",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "mvr_reports",
                "name": "MVR Reports",
                "description": "Motor Vehicle Reports for all drivers",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "section": "Commercial Auto",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "fein",
                "field_path": "first_named_insured.fein_or_ssn",
                "label": "FEIN / Tax ID",
                "section": "Commercial Auto",
                "severity": RequirementSeverity.CRITICAL,
            },
            # Vehicle Schedule fields (acord_schema uses direct arrays, not .value wrapper)
            {
                "id": "vehicle_schedule",
                "field_path": "commercial_auto.vehicle_schedule",
                "label": "Vehicle Schedule",
                "section": "Commercial Auto - Vehicles",
                "severity": RequirementSeverity.CRITICAL,
                "check_type": "array_not_empty",
            },
            {
                "id": "vehicle_vins",
                "field_path": "commercial_auto.vehicle_schedule",
                "label": "Vehicle VINs",
                "section": "Commercial Auto - Vehicles",
                "severity": RequirementSeverity.CRITICAL,
                "check_type": "array_with_field",
                "required_field": "vin",
            },
            {
                "id": "vehicle_details",
                "field_path": "commercial_auto.vehicle_schedule",
                "label": "Vehicle Year/Make/Model",
                "section": "Commercial Auto - Vehicles",
                "severity": RequirementSeverity.CRITICAL,
                "check_type": "array_with_fields",
                "required_fields": ["year", "make", "model"],
            },
            # Driver Schedule fields (acord_schema uses direct arrays, not .value wrapper)
            {
                "id": "driver_schedule",
                "field_path": "commercial_auto.driver_schedule",
                "label": "Driver Schedule",
                "section": "Commercial Auto - Drivers",
                "severity": RequirementSeverity.CRITICAL,
                "check_type": "array_not_empty",
            },
            {
                "id": "driver_license_info",
                "field_path": "commercial_auto.driver_schedule",
                "label": "Driver License Information",
                "section": "Commercial Auto - Drivers",
                "severity": RequirementSeverity.CRITICAL,
                "check_type": "array_with_fields",
                "required_fields": ["name", "license_number", "license_state"],
            },
            # Garage Locations fields (acord_schema uses direct arrays, not .value wrapper)
            {
                "id": "garage_locations",
                "field_path": "commercial_auto.garage_locations",
                "label": "Garage Locations",
                "section": "Commercial Auto - Garage",
                "severity": RequirementSeverity.IMPORTANT,
                "check_type": "array_not_empty",
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "section": "Commercial Auto",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [],
    },
    
    # =========================================================================
    # WORKERS COMPENSATION
    # =========================================================================
    "WORKERS_COMPENSATION": {
        "display_name": "Workers Compensation",
        "short_name": "WC",
        "required_documents": [
            {
                "id": "payroll_records",
                "name": "Payroll Records / Breakdown",
                "description": "Payroll breakdown by job classification/class code",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "experience_mod",
                "name": "Experience Modification Worksheet",
                "description": "Current experience mod rating documentation",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "loss_runs_5_year",
                "name": "Loss Runs (5-Year)",
                "description": "5-year workers comp claims history",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "osha_logs",
                "name": "OSHA 300 Logs",
                "description": "OSHA injury and illness logs (if 10+ employees)",
                "severity": RequirementSeverity.IMPORTANT,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "fein",
                "field_path": "first_named_insured.fein_or_ssn",
                "label": "FEIN / Tax ID",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "payroll_by_class",
                "field_path": "workers_comp.payroll_by_class_code",
                "label": "Payroll by Classification/Class Code",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "employee_count",
                "field_path": "premises[0].number_full_time_employees",
                "label": "Total Employee Count",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "experience_mod_rate",
                "field_path": "workers_comp.experience_mod_rate",
                "label": "Experience Modification Rate",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "states_of_operation",
                "field_path": "workers_comp.states",
                "label": "States Where Employees Work",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "owner_officer_payroll",
                "field_path": "workers_comp.owner_officer_payroll",
                "label": "Owner/Officer Payroll (Include/Exclude)",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [
            {
                "condition": "uses_subcontractors",
                "requires": [
                    {"id": "subcontractor_certs", "label": "Subcontractor Certificates of Insurance", "severity": RequirementSeverity.CRITICAL},
                    {"id": "subcontractor_payroll", "label": "Subcontractor Payments (Last 12 Months)", "severity": RequirementSeverity.IMPORTANT},
                ],
            },
            {
                "condition": "multi_state_operations",
                "requires": [
                    {"id": "state_payroll_breakdown", "label": "Payroll Breakdown by State", "severity": RequirementSeverity.CRITICAL},
                ],
            },
        ],
    },
    
    # =========================================================================
    # UMBRELLA / EXCESS LIABILITY
    # =========================================================================
    "UMBRELLA": {
        "display_name": "Commercial Umbrella",
        "short_name": "Umbrella",
        "required_documents": [
            {
                "id": "underlying_policies",
                "name": "Underlying Policy Declarations",
                "description": "Dec pages for all underlying policies (GL, Auto, WC, etc.)",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "loss_runs_5_year",
                "name": "Loss Runs (5-Year)",
                "description": "5-year claims history for all underlying coverages",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "underlying_limits",
                "field_path": "umbrella.underlying_limits",
                "label": "Underlying Policy Limits",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "requested_limit",
                "field_path": "umbrella.requested_limit",
                "label": "Requested Umbrella Limit",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "annual_revenue",
                "field_path": "premises[0].annual_revenues",
                "label": "Annual Revenue",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [],
    },
    
    # =========================================================================
    # BUSINESS OWNERS POLICY (BOP)
    # =========================================================================
    "BUSINESS_OWNERS": {
        "display_name": "Business Owners Policy",
        "short_name": "BOP",
        "required_documents": [
            {
                "id": "loss_runs_5_year",
                "name": "Loss Runs (5-Year)",
                "description": "5-year claims history",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "business_description",
                "field_path": "nature_of_business.description_of_primary_operations",
                "label": "Description of Business Operations",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "premises_address",
                "field_path": "premises[0].street_address",
                "label": "Business Location Address",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "annual_revenue",
                "field_path": "premises[0].annual_revenues",
                "label": "Annual Revenue",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "building_value",
                "field_path": "premises[0].building_value",
                "label": "Building Value (if owned)",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "contents_value",
                "field_path": "premises[0].contents_value",
                "label": "Contents/BPP Value",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "employee_count",
                "field_path": "premises[0].number_full_time_employees",
                "label": "Number of Employees",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [],
    },
    
    # =========================================================================
    # CYBER LIABILITY
    # =========================================================================
    "CYBER_AND_PRIVACY": {
        "display_name": "Cyber Liability",
        "short_name": "Cyber",
        "required_documents": [
            {
                "id": "cyber_questionnaire",
                "name": "Cyber Security Questionnaire",
                "description": "Completed carrier cyber security questionnaire",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "annual_revenue",
                "field_path": "premises[0].annual_revenues",
                "label": "Annual Revenue",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "pii_records",
                "field_path": "cyber.pii_records_count",
                "label": "Number of PII/PHI Records Stored",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "security_measures",
                "field_path": "cyber.security_measures",
                "label": "Current Security Measures (MFA, encryption, etc.)",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "prior_incidents",
                "field_path": "cyber.prior_incidents",
                "label": "Prior Cyber Incidents/Breaches",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [
            {
                "condition": "processes_payment_cards",
                "requires": [
                    {"id": "pci_compliance", "label": "PCI-DSS Compliance Status", "severity": RequirementSeverity.CRITICAL},
                ],
            },
            {
                "condition": "healthcare_data",
                "requires": [
                    {"id": "hipaa_compliance", "label": "HIPAA Compliance Status", "severity": RequirementSeverity.CRITICAL},
                ],
            },
        ],
    },
    
    # =========================================================================
    # PROFESSIONAL LIABILITY / E&O
    # =========================================================================
    "PROFESSIONAL_LIABILITY": {
        "display_name": "Professional Liability / E&O",
        "short_name": "E&O",
        "required_documents": [
            {
                "id": "professional_license",
                "name": "Professional License(s)",
                "description": "Copy of professional licenses for key personnel",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "sample_contracts",
                "name": "Sample Service Agreements",
                "description": "Sample client contracts showing scope of services",
                "severity": RequirementSeverity.RECOMMENDED,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "services_description",
                "field_path": "professional.services_description",
                "label": "Description of Professional Services",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "annual_revenue",
                "field_path": "premises[0].annual_revenues",
                "label": "Annual Revenue / Billings",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "years_experience",
                "field_path": "professional.years_experience",
                "label": "Years of Professional Experience",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "largest_client",
                "field_path": "professional.largest_client_percent",
                "label": "Largest Client as % of Revenue",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "prior_acts_date",
                "field_path": "professional.prior_acts_date",
                "label": "Desired Prior Acts / Retroactive Date",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [],
    },
    
    # =========================================================================
    # LIQUOR LIABILITY
    # =========================================================================
    "LIQUOR_LIABILITY": {
        "display_name": "Liquor Liability",
        "short_name": "Liquor",
        "required_documents": [
            {
                "id": "liquor_license",
                "name": "Liquor License",
                "description": "Copy of current liquor license",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "loss_runs_5_year",
                "name": "Loss Runs (5-Year)",
                "description": "5-year liquor liability claims history",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "liquor_sales",
                "field_path": "liquor.annual_liquor_sales",
                "label": "Annual Liquor Sales",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "liquor_percent",
                "field_path": "liquor.liquor_percent_of_sales",
                "label": "Liquor as % of Total Sales",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "hours_of_operation",
                "field_path": "liquor.hours_of_operation",
                "label": "Hours of Operation",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "entertainment",
                "field_path": "liquor.live_entertainment",
                "label": "Live Entertainment (Yes/No)",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [],
    },
    
    # =========================================================================
    # MOTOR CARRIER / TRUCKERS
    # =========================================================================
    "MOTOR_CARRIER": {
        "display_name": "Motor Carrier",
        "short_name": "Motor Carrier",
        "required_documents": [
            {
                "id": "vehicle_schedule",
                "name": "Power Unit & Trailer Schedule",
                "description": "Complete list of all power units and trailers with VINs",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "driver_list",
                "name": "Driver List with CDL Information",
                "description": "All drivers with CDL numbers, endorsements, hire dates",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "mvr_reports",
                "name": "MVR Reports",
                "description": "Motor Vehicle Reports for all drivers",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "loss_runs_5_year",
                "name": "Loss Runs (5-Year)",
                "description": "5-year trucking claims history",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "ifta_fuel_reports",
                "name": "IFTA Fuel Tax Reports",
                "description": "Last 4 quarters of IFTA reports",
                "severity": RequirementSeverity.IMPORTANT,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "dot_number",
                "field_path": "trucking.dot_number",
                "label": "USDOT Number",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "mc_number",
                "field_path": "trucking.mc_number",
                "label": "MC Number",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "cargo_types",
                "field_path": "trucking.cargo_types",
                "label": "Types of Cargo Hauled",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "radius",
                "field_path": "trucking.radius_of_operations",
                "label": "Radius of Operations",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "annual_mileage",
                "field_path": "trucking.annual_mileage",
                "label": "Total Annual Mileage",
                "severity": RequirementSeverity.IMPORTANT,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [
            {
                "condition": "hauls_hazmat",
                "requires": [
                    {"id": "hazmat_endorsements", "label": "Hazmat Endorsements for Drivers", "severity": RequirementSeverity.CRITICAL},
                    {"id": "hazmat_cargo_details", "label": "Hazmat Cargo Details", "severity": RequirementSeverity.CRITICAL},
                ],
            },
        ],
    },
    
    "TRUCKERS": {
        # Alias to MOTOR_CARRIER - same requirements
        "display_name": "Truckers",
        "short_name": "Truckers",
        "alias_of": "MOTOR_CARRIER",
    },
    
    # =========================================================================
    # GARAGE AND DEALERS
    # =========================================================================
    "GARAGE_AND_DEALERS": {
        "display_name": "Garage & Dealers",
        "short_name": "Garage",
        "required_documents": [
            {
                "id": "dealer_license",
                "name": "Dealer License",
                "description": "Copy of dealer license",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "inventory_list",
                "name": "Inventory Schedule",
                "description": "Current vehicle inventory with values",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "loss_runs_5_year",
                "name": "Loss Runs (5-Year)",
                "description": "5-year claims history",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "required_data": [
            {
                "id": "business_name",
                "field_path": "first_named_insured.name",
                "label": "Business Legal Name",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "operations_type",
                "field_path": "garage.operations_type",
                "label": "Type of Operations (Sales, Service, Body Shop, etc.)",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "annual_sales",
                "field_path": "premises[0].annual_revenues",
                "label": "Annual Gross Sales",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "inventory_value",
                "field_path": "garage.max_inventory_value",
                "label": "Maximum Inventory Value",
                "severity": RequirementSeverity.CRITICAL,
            },
            {
                "id": "effective_date",
                "field_path": "policy.proposed_effective_date",
                "label": "Proposed Effective Date",
                "severity": RequirementSeverity.CRITICAL,
            },
        ],
        "conditional_requirements": [],
    },
}


# =============================================================================
# UNIVERSAL REQUIREMENTS (Apply to ALL submissions)
# These are ACORD 125 critical fields that must be filled regardless of coverage
# Reference: CRITICAL_FIELD_MAPPING in pdf_field_mapping.py
# =============================================================================

UNIVERSAL_REQUIREMENTS = {
    "required_data": [
        # =====================================================================
        # FIRST NAMED INSURED (Page 1) - Most Critical
        # =====================================================================
        {
            "id": "business_name",
            "field_path": "first_named_insured.name",
            "label": "Business Legal Name",
            "section": "First Named Insured",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P1[0].NamedInsured_FullName_A[0]",
        },
        {
            "id": "mailing_address",
            "field_path": "first_named_insured.mailing_address",
            "label": "Mailing Address",
            "section": "First Named Insured",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P1[0].NamedInsured_MailingAddress_LineOne_A[0]",
        },
        {
            "id": "fein",
            "field_path": "first_named_insured.fein_or_ssn",
            "label": "FEIN / Tax ID",
            "section": "First Named Insured",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P1[0].NamedInsured_TaxIdentifier_A[0]",
        },
        {
            "id": "business_phone",
            "field_path": "first_named_insured.business_phone",
            "label": "Business Phone Number",
            "section": "First Named Insured",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P1[0].NamedInsured_Primary_PhoneNumber_A[0]",
        },
        {
            "id": "website_address",
            "field_path": "first_named_insured.website_address",
            "label": "Website Address",
            "section": "First Named Insured",
            "severity": RequirementSeverity.RECOMMENDED,
            "acord_field": "F[0].P1[0].NamedInsured_Primary_WebsiteAddress_A[0]",
        },
        {
            "id": "business_structure",
            "field_path": "first_named_insured.business_structure",
            "label": "Business Entity Type (LLC, Corp, etc.)",
            "section": "First Named Insured",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "first_named_insured_business_structure_checkbox",
        },
        
        # =====================================================================
        # POLICY INFORMATION (Page 1)
        # =====================================================================
        {
            "id": "effective_date",
            "field_path": "policy.proposed_effective_date",
            "label": "Proposed Effective Date",
            "section": "Policy",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P1[0].Policy_EffectiveDate_A[0]",
        },
        {
            "id": "expiration_date",
            "field_path": "policy.proposed_expiration_date",
            "label": "Proposed Expiration Date",
            "section": "Policy",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P1[0].Policy_ExpirationDate_A[0]",
        },
        
        # =====================================================================
        # AGENCY / PRODUCER INFORMATION (Page 1)
        # =====================================================================
        {
            "id": "agency_name",
            "field_path": "agency.name",
            "label": "Agency / Producer Name",
            "section": "Agency / Producer",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P1[0].Producer_FullName_A[0]",
        },
        {
            "id": "agency_contact_name",
            "field_path": "agency.contact_name",
            "label": "Agency Contact Name",
            "section": "Agency / Producer",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P1[0].Producer_ContactPerson_FullName_A[0]",
        },
        {
            "id": "agency_phone",
            "field_path": "agency.phone",
            "label": "Agency Phone Number",
            "section": "Agency / Producer",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P1[0].Producer_ContactPerson_PhoneNumber_A[0]",
        },
        {
            "id": "agency_email",
            "field_path": "agency.email",
            "label": "Agency Email Address",
            "section": "Agency / Producer",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P1[0].Producer_ContactPerson_EmailAddress_A[0]",
        },
        
        # =====================================================================
        # TRANSACTION STATUS (Page 1)
        # =====================================================================
        {
            "id": "transaction_type",
            "field_path": "transaction_status.type",
            "label": "Transaction Type (Quote/Renewal/Issue)",
            "section": "Transaction Status",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "transaction_status_checkbox",
        },
        
        # =====================================================================
        # LINES OF BUSINESS (Page 1)
        # =====================================================================
        {
            "id": "lines_of_business",
            "field_path": "lines_of_business",
            "label": "Lines of Business / Coverage Types",
            "section": "Lines of Business",
            "severity": RequirementSeverity.IMPORTANT,
            "check_type": "array_not_empty",
            "acord_field": "lines_of_business_checkboxes",
        },
        
        # =====================================================================
        # NATURE OF BUSINESS (Page 2)
        # =====================================================================
        {
            "id": "business_description",
            "field_path": "nature_of_business.description_of_primary_operations",
            "label": "Description of Operations",
            "section": "Nature of Business",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P2[0].CommercialPolicy_OperationsDescription_A[0]",
        },
        {
            "id": "business_start_date",
            "field_path": "nature_of_business.date_business_started",
            "label": "Date Business Started",
            "section": "Nature of Business",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P2[0].NamedInsured_BusinessStartDate_A[0]",
        },
        {
            "id": "business_type",
            "field_path": "nature_of_business.business_type",
            "label": "Business Type (Restaurant, Retail, Office, etc.)",
            "section": "Nature of Business",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "nature_of_business_business_type_checkboxes",
        },
        
        # =====================================================================
        # CONTACT INFORMATION (Page 2)
        # =====================================================================
        {
            "id": "primary_contact",
            "field_path": "contacts",
            "label": "At Least One Contact",
            "section": "Contacts",
            "severity": RequirementSeverity.IMPORTANT,
            "check_type": "array_not_empty",
        },
        {
            "id": "contact_type",
            "field_path": "contacts[0].contact_type",
            "label": "Contact Type / Title",
            "section": "Contacts",
            "severity": RequirementSeverity.RECOMMENDED,
            "acord_field": "F[0].P2[0].NamedInsured_Contact_ContactDescription_A[0]",
        },
        {
            "id": "contact_name",
            "field_path": "contacts[0].contact_name",
            "label": "Contact Name",
            "section": "Contacts",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P2[0].NamedInsured_Contact_FullName_A[0]",
        },
        {
            "id": "contact_phone",
            "field_path": "contacts[0].primary_phone",
            "label": "Contact Phone Number",
            "section": "Contacts",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P2[0].NamedInsured_Contact_PrimaryPhoneNumber_A[0]",
        },
        {
            "id": "contact_email",
            "field_path": "contacts[0].primary_email",
            "label": "Contact Email Address",
            "section": "Contacts",
            "severity": RequirementSeverity.RECOMMENDED,
            "acord_field": "F[0].P2[0].NamedInsured_Contact_PrimaryEmailAddress_A[0]",
        },
        
        # =====================================================================
        # PREMISES INFORMATION (Page 2) - At least one location required
        # =====================================================================
        {
            "id": "premises_location",
            "field_path": "premises",
            "label": "At Least One Premises Location",
            "section": "Premises Information",
            "severity": RequirementSeverity.CRITICAL,
            "check_type": "array_not_empty",
        },
        {
            "id": "premises_street",
            "field_path": "premises[0].street_address",
            "label": "Street Address",
            "section": "Premises Information",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P2[0].CommercialStructure_PhysicalAddress_LineOne_A[0]",
        },
        {
            "id": "premises_city",
            "field_path": "premises[0].city",
            "label": "City",
            "section": "Premises Information",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P2[0].CommercialStructure_PhysicalAddress_CityName_A[0]",
        },
        {
            "id": "premises_state",
            "field_path": "premises[0].state",
            "label": "State",
            "section": "Premises Information",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P2[0].CommercialStructure_PhysicalAddress_StateOrProvinceCode_A[0]",
        },
        {
            "id": "premises_zip",
            "field_path": "premises[0].zip",
            "label": "ZIP Code",
            "section": "Premises Information",
            "severity": RequirementSeverity.CRITICAL,
            "acord_field": "F[0].P2[0].CommercialStructure_PhysicalAddress_PostalCode_A[0]",
        },
        {
            "id": "full_time_employees",
            "field_path": "premises[0].number_full_time_employees",
            "label": "Number of Full-Time Employees",
            "section": "Premises Information",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P2[0].BusinessInformation_FullTimeEmployeeCount_A[0]",
        },
        {
            "id": "part_time_employees",
            "field_path": "premises[0].number_part_time_employees",
            "label": "Number of Part-Time Employees",
            "section": "Premises Information",
            "severity": RequirementSeverity.RECOMMENDED,
            "acord_field": "F[0].P2[0].BusinessInformation_PartTimeEmployeeCount_A[0]",
        },
        {
            "id": "annual_revenue",
            "field_path": "premises[0].annual_revenues",
            "label": "Annual Revenue / Gross Sales",
            "section": "Premises Information",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "F[0].P2[0].CommercialStructure_AnnualRevenueAmount_A[0]",
        },
        {
            "id": "occupied_area",
            "field_path": "premises[0].occupied_area_sq_ft",
            "label": "Occupied Area (Sq. Ft.)",
            "section": "Premises Information",
            "severity": RequirementSeverity.RECOMMENDED,
            "acord_field": "F[0].P2[0].BuildingOccupancy_OccupiedArea_A[0]",
        },
        {
            "id": "premises_operations",
            "field_path": "premises[0].description_of_operations",
            "label": "Description of Operations at Location",
            "section": "Premises Information",
            "severity": RequirementSeverity.RECOMMENDED,
            "acord_field": "F[0].P2[0].BuildingOccupancy_OperationsDescription_A[0]",
        },
        {
            "id": "premises_interest",
            "field_path": "premises[0].interest",
            "label": "Interest (Owner/Tenant)",
            "section": "Premises Information",
            "severity": RequirementSeverity.IMPORTANT,
            "acord_field": "premises_interest_checkbox_0",
        },
    ],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_requirements_for_coverages(coverage_types: List[str]) -> Dict[str, Any]:
    """
    Get combined requirements for a list of coverage types.
    
    Args:
        coverage_types: List of coverage type strings (e.g., ["COMMERCIAL_GENERAL_LIABILITY", "BUSINESS_AUTO"])
        
    Returns:
        Dictionary with combined requirements
    """
    combined = {
        "required_documents": [],
        "required_data": [],
        "conditional_requirements": [],
        "coverage_types": coverage_types,
    }
    
    seen_doc_ids = set()
    seen_data_ids = set()
    
    # Add universal requirements first
    for req in UNIVERSAL_REQUIREMENTS.get("required_data", []):
        if req["id"] not in seen_data_ids:
            combined["required_data"].append(req)
            seen_data_ids.add(req["id"])
    
    # Add coverage-specific requirements
    for coverage in coverage_types:
        coverage_upper = coverage.upper().replace(" ", "_")
        
        if coverage_upper not in COVERAGE_REQUIREMENTS:
            continue
            
        reqs = COVERAGE_REQUIREMENTS[coverage_upper]
        
        # Handle aliases
        if "alias_of" in reqs:
            reqs = COVERAGE_REQUIREMENTS[reqs["alias_of"]]
        
        # Add documents
        for doc in reqs.get("required_documents", []):
            if doc["id"] not in seen_doc_ids:
                doc_with_coverage = {**doc, "for_coverage": coverage_upper}
                combined["required_documents"].append(doc_with_coverage)
                seen_doc_ids.add(doc["id"])
        
        # Add data fields
        for data in reqs.get("required_data", []):
            if data["id"] not in seen_data_ids:
                data_with_coverage = {**data, "for_coverage": coverage_upper}
                combined["required_data"].append(data_with_coverage)
                seen_data_ids.add(data["id"])
        
        # Add conditional requirements
        for cond in reqs.get("conditional_requirements", []):
            cond_with_coverage = {**cond, "for_coverage": coverage_upper}
            combined["conditional_requirements"].append(cond_with_coverage)
    
    return combined


def get_all_coverage_types() -> List[Dict[str, str]]:
    """Get list of all supported coverage types with display names."""
    return [
        {
            "code": key,
            "display_name": value.get("display_name", key),
            "short_name": value.get("short_name", key),
        }
        for key, value in COVERAGE_REQUIREMENTS.items()
        if "alias_of" not in value
    ]










