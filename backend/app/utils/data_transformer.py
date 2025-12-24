"""
Data transformation utilities for ACORD schema mapping
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import date, datetime

logger = logging.getLogger(__name__)


def unwrap_confidence_objects(data: Any) -> Any:
    """
    Recursively unwrap confidence objects to extract raw values
    
    Transforms:
        {"value": <data>, "confidence": 0.95} -> <data>
    
    Args:
        data: Nested data structure with confidence wrappers
        
    Returns:
        Unwrapped data structure with raw values
    """
    if data is None:
        return None
    
    # Handle dict with confidence wrapper
    if isinstance(data, dict):
        # Check if this is a confidence-wrapped field
        if 'value' in data and 'confidence' in data:
            # Extract the raw value and recursively unwrap it
            return unwrap_confidence_objects(data['value'])
        else:
            # Regular dict - recursively unwrap all values
            return {
                key: unwrap_confidence_objects(value)
                for key, value in data.items()
            }
    
    # Handle list - recursively unwrap all items
    elif isinstance(data, list):
        return [unwrap_confidence_objects(item) for item in data]
    
    # Base case - return raw value
    else:
        return data


def coerce_to_bool(value: Any, default: Optional[bool] = None) -> Optional[bool]:
    """
    Convert various representations of boolean values into actual booleans.
    
    Args:
        value: Input value to convert
        default: Default value if conversion fails
        
    Returns:
        Converted boolean or default if conversion not possible
    """
    if isinstance(value, bool):
        return value
    
    if value is None:
        return default
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"yes", "true", "1", "y", "t"}:
            return True
        if normalized in {"no", "false", "0", "n", "f"}:
            return False
    
    return default


def normalize_interest(value: Any) -> Optional[str]:
    """
    Normalize premises interest values to OWNER or TENANT.
    """
    if value is None:
        return None
    
    if hasattr(value, "value"):
        value = getattr(value, "value")
    
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in {"OWNER", "TENANT"}:
            return normalized
        if normalized in {"OWN", "OWNED"}:
            return "OWNER"
        if normalized in {"RENT", "LEASE", "TEN"}:
            return "TENANT"
    
    return None


def transform_lines_of_business(raw_lines: Any, prior_carriers: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Transform lines of business from simple list to schema-compliant objects
    
    Line of Business = What insurance coverage types the client is requesting
    (e.g., General Liability, Commercial Property, Business Auto, etc.)
    
    Transforms:
        ["COMMERCIAL_GENERAL_LIABILITY", "BUSINESS_AUTO"]
    To:
        [
            {"line": "COMMERCIAL_GENERAL_LIABILITY", "selected": true},
            {"line": "BUSINESS_AUTO", "selected": true}
        ]
    
    Args:
        raw_lines: List of line of business strings or existing objects
        
    Returns:
        List of properly structured line of business objects
    """
    if not raw_lines:
        return []
    
    # If already in correct format, return as is
    if isinstance(raw_lines, list) and len(raw_lines) > 0:
        if isinstance(raw_lines[0], dict) and 'line' in raw_lines[0]:
            return raw_lines
    
    # Convert list of strings to proper schema objects
    result = []
    if isinstance(raw_lines, list):
        for line in raw_lines:
            line_str = str(line).upper().strip()
            result.append({
                'line': line_str,
                'selected': True
            })
    
    return result


def transform_contacts(raw_contacts: Any) -> List[Dict[str, Any]]:
    """
    Transform contacts to schema-compliant format
    
    Handles various contact formats and normalizes them
    
    Args:
        raw_contacts: Raw contact data in various formats
        
    Returns:
        List of properly structured contact objects
    """
    if not raw_contacts:
        return []
    
    if not isinstance(raw_contacts, list):
        return []
    
    result = []
    for contact in raw_contacts:
        if isinstance(contact, dict):
            # Map different field names to schema fields
            result.append({
                'contact_type': contact.get('type') or contact.get('contact_type'),
                'contact_name': contact.get('name') or contact.get('contact_name'),
                'primary_email': contact.get('email') or contact.get('primary_email'),
                'secondary_email': contact.get('secondary_email'),
                'primary_phone': contact.get('phone') or contact.get('primary_phone'),
                'primary_phone_type': contact.get('phone_type') or contact.get('primary_phone_type', 'BUSINESS'),
                'secondary_phone': contact.get('secondary_phone'),
                'secondary_phone_type': contact.get('secondary_phone_type')
            })
    
    return result


def transform_other_named_insureds(raw_insureds: Any) -> List[Dict[str, Any]]:
    """
    Transform other named insureds to schema-compliant format.
    
    Args:
        raw_insureds: Raw list of other named insured entries
        
    Returns:
        List of normalized other named insured objects
    """
    if not raw_insureds:
        return []
    
    if not isinstance(raw_insureds, list):
        return []
    
    result = []
    for insured in raw_insureds:
        if isinstance(insured, dict):
            result.append({
                'name': insured.get('name'),
                'mailing_address': insured.get('mailing_address') or insured.get('address'),
                'business_structure': insured.get('business_structure'),
                'number_of_members': insured.get('number_of_members'),
                'number_of_managers': insured.get('number_of_managers'),
                'naics_code': insured.get('naics_code'),
                'sic_code': insured.get('sic_code'),
                'gl_code': insured.get('gl_code'),
                'fein_or_ssn': insured.get('fein_or_ssn'),
                'business_phone': insured.get('business_phone') or insured.get('phone'),
                'website_address': insured.get('website_address') or insured.get('website'),
            })
    
    return result


def transform_premises(raw_premises: Any) -> List[Dict[str, Any]]:
    """
    Transform premises to schema-compliant format
    
    Args:
        raw_premises: Raw premises data
        
    Returns:
        List of properly structured premise objects
    """
    if not raw_premises:
        return []
    
    if not isinstance(raw_premises, list):
        return []
    
    result = []
    for idx, premise in enumerate(raw_premises, 1):
        if isinstance(premise, dict):
            # Map fields and add missing schema fields
            transformed = {
                'location_number': premise.get('location_number', idx),
                'building_number': premise.get('building_number'),
                'street_address': premise.get('street_address'),
                'city': premise.get('city'),
                'county': premise.get('county'),
                'state': premise.get('state'),
                'zip': premise.get('zip'),
                'city_limits': coerce_to_bool(premise.get('city_limits'), False),
                'description_of_operations': premise.get('operations_description') or premise.get('description_of_operations'),
                'interest': normalize_interest(premise.get('interest')),
                'owner_or_tenant_inside': coerce_to_bool(premise.get('owner_or_tenant_inside'), False),
                'owner_or_tenant_outside': coerce_to_bool(premise.get('owner_or_tenant_outside'), False),
                'number_full_time_employees': premise.get('full_time_employees') or premise.get('number_full_time_employees') or premise.get('employees'),
                'number_part_time_employees': premise.get('part_time_employees') or premise.get('number_part_time_employees'),
                'annual_revenues': premise.get('revenues') or premise.get('annual_revenues'),
                'occupied_area_sq_ft': premise.get('square_footage') or premise.get('occupied_area_sq_ft'),
                'total_building_area_sq_ft': premise.get('total_building_area_sq_ft'),
                'open_to_public_area_sq_ft': premise.get('open_to_public_area_sq_ft'),
                'any_area_leased_to_others': coerce_to_bool(premise.get('any_area_leased_to_others'), False)
            }
            result.append(transformed)
    
    return result


def transform_prior_carriers(raw_carriers: Any) -> List[Dict[str, Any]]:
    """
    Transform prior carriers to schema-compliant format
    
    Args:
        raw_carriers: Raw prior carrier data
        
    Returns:
        List of properly structured carrier objects
    """
    if not raw_carriers:
        return []
    
    if not isinstance(raw_carriers, list):
        return []
    
    result = []
    for carrier in raw_carriers:
        if isinstance(carrier, dict):
            # Parse effective/expiration dates if combined
            effective_date = carrier.get('effective_date')
            expiration_date = carrier.get('expiration_date')
            
            # Handle combined date field like "2025-01-01/2026-01-01"
            if not effective_date and 'effective/expiration_dates' in carrier:
                date_range = carrier['effective/expiration_dates']
                if isinstance(date_range, str) and '/' in date_range:
                    parts = date_range.split('/')
                    if len(parts) == 2:
                        effective_date = parts[0].strip()
                        expiration_date = parts[1].strip()
            
            # Determine carrier category from policy number or type
            category = carrier.get('category')
            if not category:
                policy_number = str(carrier.get('policy_number', '')).upper()
                if 'GL' in policy_number or 'GENERAL' in policy_number:
                    category = 'GENERAL_LIABILITY'
                elif 'CP' in policy_number or 'PROPERTY' in policy_number:
                    category = 'PROPERTY'
                elif 'CA' in policy_number or 'AUTO' in policy_number:
                    category = 'AUTOMOBILE'
                elif 'WC' in policy_number or 'WORKERS' in policy_number:
                    category = 'WORKERS_COMPENSATION'
            
            result.append({
                'category': category,
                'carrier_name': carrier.get('carrier_name'),
                'policy_number': carrier.get('policy_number'),
                'effective_date': effective_date,
                'expiration_date': expiration_date,
                'premium': carrier.get('premium'),
                'years_with_carrier': carrier.get('years_with_carrier')
            })
    
    return result


def transform_losses(raw_losses: Any) -> List[Dict[str, Any]]:
    """
    Transform losses to schema-compliant format
    
    Args:
        raw_losses: Raw loss data
        
    Returns:
        List of properly structured loss objects
    """
    if not raw_losses:
        return []
    
    if not isinstance(raw_losses, list):
        return []
    
    result = []
    for loss in raw_losses:
        if isinstance(loss, dict):
            result.append({
                'date_of_loss': loss.get('date') or loss.get('date_of_loss'),
                'line_type': loss.get('line_type'),
                'description_of_occurrence': loss.get('description') or loss.get('description_of_occurrence'),
                'amount_paid': loss.get('amounts_paid') or loss.get('amount_paid'),
                'amount_reserved': loss.get('reserved') or loss.get('amount_reserved'),
                'claim_open': loss.get('claim_open', False),
                'subrogation': loss.get('subrogation', False)
            })
    
    return result


def transform_extracted_to_acord_schema(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform extracted data with confidence wrappers to ACORD-compliant schema
    
    This is the main transformation function that:
    1. Unwraps all confidence objects
    2. Restructures data to match ACORD schema
    3. Maps field names appropriately
    
    Args:
        extracted_data: Raw extracted data with confidence wrappers
        
    Returns:
        ACORD-compliant schema data
    """
    try:
        logger.info("Transforming extracted data to ACORD schema")
        
        # Step 1: Unwrap all confidence objects
        unwrapped = unwrap_confidence_objects(extracted_data)
        
        # Step 2: Transform specific sections
        acord_data = {}
        
        # Agency - direct mapping
        if 'agency' in unwrapped:
            acord_data['agency'] = unwrapped['agency']
        
        # Transaction Status - direct mapping
        if 'transaction_status' in unwrapped:
            acord_data['transaction_status'] = unwrapped['transaction_status']
        
        # Policy - direct mapping
        if 'policy' in unwrapped:
            acord_data['policy'] = unwrapped['policy']
        
        # Lines of Business - transform from list to objects
        if 'lines_of_business' in unwrapped:
            prior_carriers = unwrapped.get('prior_carriers', [])
            acord_data['lines_of_business'] = transform_lines_of_business(
                unwrapped['lines_of_business'],
                prior_carriers
            )
        
        # First Named Insured - direct mapping
        if 'first_named_insured' in unwrapped:
            acord_data['first_named_insured'] = unwrapped['first_named_insured']
        
        # Other Named Insureds - transform format
        if 'other_named_insureds' in unwrapped:
            acord_data['other_named_insureds'] = transform_other_named_insureds(unwrapped['other_named_insureds'])
        
        # Contacts - transform format
        if 'contacts' in unwrapped:
            acord_data['contacts'] = transform_contacts(unwrapped['contacts'])
        
        # Nature of Business - direct mapping
        if 'nature_of_business' in unwrapped:
            acord_data['nature_of_business'] = unwrapped['nature_of_business']
        
        # Premises - transform and normalize
        if 'premises' in unwrapped:
            acord_data['premises'] = transform_premises(unwrapped['premises'])
        
        # Prior Carriers - transform dates
        if 'prior_carriers' in unwrapped:
            acord_data['prior_carriers'] = transform_prior_carriers(unwrapped['prior_carriers'])
        
        # Loss History - transform losses
        if 'loss_history' in unwrapped:
            loss_history = unwrapped['loss_history'].copy()
            if 'losses' in loss_history:
                loss_history['losses'] = transform_losses(loss_history['losses'])
            acord_data['loss_history'] = loss_history
        
        # Signatures - direct mapping
        if 'signatures' in unwrapped:
            acord_data['signatures'] = unwrapped['signatures']
        
        # =====================================================================
        # PHASE 2: Form-Specific Sections (pass through from merged extraction)
        # =====================================================================
        
        # ACORD 126 - General Liability
        if 'general_liability' in unwrapped:
            acord_data['general_liability'] = unwrapped['general_liability']
            logger.info("Included general_liability (ACORD 126) data in ACORD schema")
        
        # ACORD 127 - Commercial Auto
        if 'commercial_auto' in unwrapped:
            acord_data['commercial_auto'] = unwrapped['commercial_auto']
            logger.info("Included commercial_auto (ACORD 127) data in ACORD schema")
        
        # ACORD 130 - Workers Compensation
        if 'workers_compensation' in unwrapped:
            acord_data['workers_compensation'] = unwrapped['workers_compensation']
            logger.info("Included workers_compensation (ACORD 130) data in ACORD schema")
        
        # ACORD 140 - Commercial Property
        if 'property' in unwrapped:
            acord_data['property'] = unwrapped['property']
            logger.info("Included property (ACORD 140) data in ACORD schema")
        
        # Add metadata
        acord_data['extraction_timestamp'] = datetime.utcnow().isoformat()
        acord_data['validation_status'] = 'extracted'
        
        logger.info("Successfully transformed data to ACORD schema")
        return acord_data
        
    except Exception as e:
        logger.error(f"Failed to transform data to ACORD schema: {str(e)}", exc_info=True)
        # Return empty schema on error
        return {
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'validation_status': 'error',
            'error_message': str(e)
        }



