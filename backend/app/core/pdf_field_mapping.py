"""
Mapping from ACORD 125 schema fields to PDF AcroForm field names.

Only 15–20 critical fields are targeted for MVP.
"""

from typing import Dict, Any


# Schema path -> PDF field name
# Mapped to actual ACORD 125 fillable PDF field names
CRITICAL_FIELD_MAPPING: Dict[str, str] = {
    # First Named Insured (Page 1)
    "first_named_insured.name": "F[0].P1[0].NamedInsured_FullName_A[0]",
    "first_named_insured.mailing_address": "F[0].P1[0].NamedInsured_MailingAddress_LineOne_A[0]",
    "first_named_insured.fein_or_ssn": "F[0].P1[0].NamedInsured_TaxIdentifier_A[0]",
    "first_named_insured.business_phone": "F[0].P1[0].NamedInsured_Primary_PhoneNumber_A[0]",
    "first_named_insured.website_address": "F[0].P1[0].NamedInsured_Primary_WebsiteAddress_A[0]",
    
    # Business Structure (checkboxes)
    "first_named_insured.business_structure": "first_named_insured_business_structure_checkbox",  # Will be handled specially

    # Policy (Page 1)
    "policy.proposed_effective_date": "F[0].P1[0].Policy_EffectiveDate_A[0]",
    "policy.proposed_expiration_date": "F[0].P1[0].Policy_ExpirationDate_A[0]",

    # Agency/Producer (Page 1)
    "agency.name": "F[0].P1[0].Producer_FullName_A[0]",
    "agency.contact_name": "F[0].P1[0].Producer_ContactPerson_FullName_A[0]",
    "agency.phone": "F[0].P1[0].Producer_ContactPerson_PhoneNumber_A[0]",
    "agency.email": "F[0].P1[0].Producer_ContactPerson_EmailAddress_A[0]",

    # Transaction Status (checkboxes on Page 1)
    "transaction_status.type": "transaction_status_checkbox",  # Placeholder handled specially

    # Lines of Business (checkboxes on Page 1)
    "lines_of_business": "lines_of_business_checkboxes",  # Placeholder handled specially

    # Nature of Business (Page 2)
    "nature_of_business.description_of_primary_operations": "F[0].P2[0].CommercialPolicy_OperationsDescription_A[0]",
    "nature_of_business.date_business_started": "F[0].P2[0].NamedInsured_BusinessStartDate_A[0]",
    "nature_of_business.business_type": "nature_of_business_business_type_checkboxes",  # Placeholder handled specially

    # Contact Information (Page 2 - first two contacts)
    "contacts[0].contact_type": "F[0].P2[0].NamedInsured_Contact_ContactDescription_A[0]",
    "contacts[0].contact_name": "F[0].P2[0].NamedInsured_Contact_FullName_A[0]",
    "contacts[0].primary_phone": "F[0].P2[0].NamedInsured_Contact_PrimaryPhoneNumber_A[0]",
    "contacts[0].secondary_phone": "F[0].P2[0].NamedInsured_Contact_SecondaryPhoneNumber_A[0]",
    "contacts[0].primary_email": "F[0].P2[0].NamedInsured_Contact_PrimaryEmailAddress_A[0]",
    "contacts[0].secondary_email": "F[0].P2[0].NamedInsured_Contact_SecondaryEmailAddress_A[0]",
    "contacts[1].contact_type": "F[0].P2[0].NamedInsured_Contact_ContactDescription_B[0]",
    "contacts[1].contact_name": "F[0].P2[0].NamedInsured_Contact_FullName_B[0]",
    "contacts[1].primary_phone": "F[0].P2[0].NamedInsured_Contact_PrimaryPhoneNumber_B[0]",
    "contacts[1].secondary_phone": "F[0].P2[0].NamedInsured_Contact_SecondaryPhoneNumber_B[0]",
    "contacts[1].primary_email": "F[0].P2[0].NamedInsured_Contact_PrimaryEmailAddress_B[0]",
    "contacts[1].secondary_email": "F[0].P2[0].NamedInsured_Contact_SecondaryEmailAddress_B[0]",

    # Premises (Page 2)
    "premises[0].street_address": "F[0].P2[0].CommercialStructure_PhysicalAddress_LineOne_A[0]",
    "premises[0].city": "F[0].P2[0].CommercialStructure_PhysicalAddress_CityName_A[0]",
    "premises[0].state": "F[0].P2[0].CommercialStructure_PhysicalAddress_StateOrProvinceCode_A[0]",
    "premises[0].zip": "F[0].P2[0].CommercialStructure_PhysicalAddress_PostalCode_A[0]",
    "premises[0].number_full_time_employees": "F[0].P2[0].BusinessInformation_FullTimeEmployeeCount_A[0]",
    "premises[0].number_part_time_employees": "F[0].P2[0].BusinessInformation_PartTimeEmployeeCount_A[0]",
    "premises[0].annual_revenues": "F[0].P2[0].CommercialStructure_AnnualRevenueAmount_A[0]",
    "premises[0].occupied_area_sq_ft": "F[0].P2[0].BuildingOccupancy_OccupiedArea_A[0]",
    "premises[0].description_of_operations": "F[0].P2[0].BuildingOccupancy_OperationsDescription_A[0]",
    "premises[0].interest": "premises_interest_checkbox_0",
    "premises[1].street_address": "F[0].P2[0].CommercialStructure_PhysicalAddress_LineOne_B[0]",
    "premises[1].city": "F[0].P2[0].CommercialStructure_PhysicalAddress_CityName_B[0]",
    "premises[1].state": "F[0].P2[0].CommercialStructure_PhysicalAddress_StateOrProvinceCode_B[0]",
    "premises[1].zip": "F[0].P2[0].CommercialStructure_PhysicalAddress_PostalCode_B[0]",
    "premises[1].number_full_time_employees": "F[0].P2[0].BusinessInformation_FullTimeEmployeeCount_B[0]",
    "premises[1].number_part_time_employees": "F[0].P2[0].BusinessInformation_PartTimeEmployeeCount_B[0]",
    "premises[1].annual_revenues": "F[0].P2[0].CommercialStructure_AnnualRevenueAmount_B[0]",
    "premises[1].occupied_area_sq_ft": "F[0].P2[0].BuildingOccupancy_OccupiedArea_B[0]",
    "premises[1].description_of_operations": "F[0].P2[0].BuildingOccupancy_OperationsDescription_B[0]",
    "premises[1].interest": "premises_interest_checkbox_1",
    "premises[2].street_address": "F[0].P2[0].CommercialStructure_PhysicalAddress_LineOne_C[0]",
    "premises[2].city": "F[0].P2[0].CommercialStructure_PhysicalAddress_CityName_C[0]",
    "premises[2].state": "F[0].P2[0].CommercialStructure_PhysicalAddress_StateOrProvinceCode_C[0]",
    "premises[2].zip": "F[0].P2[0].CommercialStructure_PhysicalAddress_PostalCode_C[0]",
    "premises[2].number_full_time_employees": "F[0].P2[0].BusinessInformation_FullTimeEmployeeCount_C[0]",
    "premises[2].number_part_time_employees": "F[0].P2[0].BusinessInformation_PartTimeEmployeeCount_C[0]",
    "premises[2].annual_revenues": "F[0].P2[0].CommercialStructure_AnnualRevenueAmount_C[0]",
    "premises[2].occupied_area_sq_ft": "F[0].P2[0].BuildingOccupancy_OccupiedArea_C[0]",
    "premises[2].description_of_operations": "F[0].P2[0].BuildingOccupancy_OperationsDescription_C[0]",
    "premises[2].interest": "premises_interest_checkbox_2",
    "premises[3].street_address": "F[0].P2[0].CommercialStructure_PhysicalAddress_LineOne_D[0]",
    "premises[3].city": "F[0].P2[0].CommercialStructure_PhysicalAddress_CityName_D[0]",
    "premises[3].state": "F[0].P2[0].CommercialStructure_PhysicalAddress_StateOrProvinceCode_D[0]",
    "premises[3].zip": "F[0].P2[0].CommercialStructure_PhysicalAddress_PostalCode_D[0]",
    "premises[3].number_full_time_employees": "F[0].P2[0].BusinessInformation_FullTimeEmployeeCount_D[0]",
    "premises[3].number_part_time_employees": "F[0].P2[0].BusinessInformation_PartTimeEmployeeCount_D[0]",
    "premises[3].annual_revenues": "F[0].P2[0].CommercialStructure_AnnualRevenueAmount_D[0]",
    "premises[3].occupied_area_sq_ft": "F[0].P2[0].BuildingOccupancy_OccupiedArea_D[0]",
    "premises[3].description_of_operations": "F[0].P2[0].BuildingOccupancy_OperationsDescription_D[0]",
    "premises[3].interest": "premises_interest_checkbox_3",
}


# Mapping of transaction status enum values to their checkbox field names
TRANSACTION_STATUS_CHECKBOX_MAPPING: Dict[str, str] = {
    "QUOTE": "F[0].P1[0].Policy_Status_QuoteIndicator_A[0]",
    "ISSUE_POLICY": "F[0].P1[0].Policy_Status_IssueIndicator_A[0]",
    "RENEWAL": "F[0].P1[0].Policy_Status_RenewIndicator_A[0]",
    "BOUND": "F[0].P1[0].Policy_Status_BoundIndicator_A[0]",
    "CHANGE": "F[0].P1[0].Policy_Status_ChangeIndicator_A[0]",
    "CANCEL": "F[0].P1[0].Policy_Status_CancelIndicator_A[0]",
}

TRANSACTION_STATUS_NORMALIZATION: Dict[str, str] = {
    "RENEW": "RENEWAL",
    "RENEWED": "RENEWAL",
    "RENEWING": "RENEWAL",
    "ISSUE": "ISSUE_POLICY",
    "ISSUED": "ISSUE_POLICY",
    "NEW": "ISSUE_POLICY",
    "NEW_BUSINESS": "ISSUE_POLICY",
    "ENDORSE": "CHANGE",
    "ENDORSEMENT": "CHANGE",
}


LINE_OF_BUSINESS_CHECKBOX_MAPPING: Dict[str, str] = {
    "COMMERCIAL_GENERAL_LIABILITY": "F[0].P1[0].Policy_LineOfBusiness_CommercialGeneralLiability_A[0]",
    "COMMERCIAL_PROPERTY": "F[0].P1[0].Policy_LineOfBusiness_CommercialProperty_A[0]",
    "BUSINESS_AUTO": "F[0].P1[0].Policy_LineOfBusiness_BusinessAutoIndicator_A[0]",
    "UMBRELLA": "F[0].P1[0].Policy_LineOfBusiness_UmbrellaIndicator_A[0]",
    "BUSINESS_OWNERS": "F[0].P1[0].Policy_LineOfBusiness_BusinessOwnersIndicator_A[0]",
    "GARAGE_AND_DEALERS": "F[0].P1[0].Policy_LineOfBusiness_GarageAndDealersIndicator_A[0]",
    "CRIME": "F[0].P1[0].Policy_LineOfBusiness_CrimeIndicator_A[0]",
    "BOILER_AND_MACHINERY": "F[0].P1[0].Policy_LineOfBusiness_BoilerAndMachineryIndicator_A[0]",
    "COMMERCIAL_INLAND_MARINE": "F[0].P1[0].Policy_LineOfBusiness_CommercialInlandMarineIndicator_A[0]",
    "CYBER_AND_PRIVACY": "F[0].P1[0].Policy_LineOfBusiness_CyberAndPrivacy_A[0]",
    "FIDUCIARY_LIABILITY": "F[0].P1[0].Policy_LineOfBusiness_FiduciaryLiabilityIndicator_A[0]",
    "LIQUOR_LIABILITY": "F[0].P1[0].Policy_LineOfBusiness_LiquorLiabilityIndicator_A[0]",
    "MOTOR_CARRIER": "F[0].P1[0].Policy_LineOfBusiness_MotorCarrierIndicator_A[0]",
    "TRUCKERS": "F[0].P1[0].Policy_LineOfBusiness_TruckersIndicator_A[0]",
    "YACHT": "F[0].P1[0].Policy_LineOfBusiness_YachtIndicator_A[0]",
}


NATURE_OF_BUSINESS_TYPE_CHECKBOX_MAPPING: Dict[str, str] = {
    "apartments": "F[0].P2[0].BusinessInformation_BusinessType_ApartmentsIndicator_A[0]",
    "condominiums": "F[0].P2[0].BusinessInformation_BusinessType_CondominiumsIndicator_A[0]",
    "condominium": "F[0].P2[0].BusinessInformation_BusinessType_CondominiumsIndicator_A[0]",
    "contractor": "F[0].P2[0].BusinessInformation_BusinessType_ContractorIndicator_A[0]",
    "institutional": "F[0].P2[0].BusinessInformation_BusinessType_InstitutionalIndicator_A[0]",
    "manufacturing": "F[0].P2[0].BusinessInformation_BusinessType_ManufacturingIndicator_A[0]",
    "office": "F[0].P2[0].BusinessInformation_BusinessType_OfficeIndicator_A[0]",
    "restaurant": "F[0].P2[0].BusinessInformation_BusinessType_RestaurantIndicator_A[0]",
    "retail": "F[0].P2[0].BusinessInformation_BusinessType_RetailIndicator_A[0]",
    "service": "F[0].P2[0].BusinessInformation_BusinessType_ServiceIndicator_A[0]",
    "wholesale": "F[0].P2[0].BusinessInformation_BusinessType_WholesaleIndicator_A[0]",
    "other": "F[0].P2[0].BusinessInformation_BusinessType_OtherIndicator_A[0]",
}

PREMISES_INTEREST_CHECKBOX_MAPPING: Dict[int, Dict[str, str]] = {
    0: {
        "owner": "F[0].P2[0].CommercialStructure_InsuredInterest_OwnerIndicator_A[0]",
        "tenant": "F[0].P2[0].CommercialStructure_InsuredInterest_TenantIndicator_A[0]",
    },
    1: {
        "owner": "F[0].P2[0].CommercialStructure_InsuredInterest_OwnerIndicator_B[0]",
        "tenant": "F[0].P2[0].CommercialStructure_InsuredInterest_TenantIndicator_B[0]",
    },
    2: {
        "owner": "F[0].P2[0].CommercialStructure_InsuredInterest_OwnerIndicator_C[0]",
        "tenant": "F[0].P2[0].CommercialStructure_InsuredInterest_TenantIndicator_C[0]",
    },
    3: {
        "owner": "F[0].P2[0].CommercialStructure_InsuredInterest_OwnerIndicator_D[0]",
        "tenant": "F[0].P2[0].CommercialStructure_InsuredInterest_TenantIndicator_D[0]",
    },
}


BUSINESS_STRUCTURE_CHECKBOX_MAPPING: Dict[str, str] = {
    "INDIVIDUAL": "F[0].P1[0].NamedInsured_LegalEntity_IndividualIndicator_A[0]",
    "PARTNERSHIP": "F[0].P1[0].NamedInsured_LegalEntity_PartnershipIndicator_A[0]",
    "CORPORATION": "F[0].P1[0].NamedInsured_LegalEntity_CorporationIndicator_A[0]",
    "LLC": "F[0].P1[0].NamedInsured_LegalEntity_LimitedLiabilityCorporationIndicator_A[0]",
    "JOINT_VENTURE": "F[0].P1[0].NamedInsured_LegalEntity_JointVentureIndicator_A[0]",
    "NOT_FOR_PROFIT_ORG": "F[0].P1[0].NamedInsured_LegalEntity_NotForProfitIndicator_A[0]",
    "SUBCHAPTER_S_CORPORATION": "F[0].P1[0].NamedInsured_LegalEntity_SubchapterSCorporationIndicator_A[0]",
    "TRUST": "F[0].P1[0].NamedInsured_LegalEntity_TrustIndicator_A[0]",
    "OTHER": "F[0].P1[0].NamedInsured_LegalEntity_OtherIndicator_A[0]",
}


def format_value_for_pdf(field_path: str, value: Any) -> str:
    """Light formatting for common types before placing into PDF fields."""
    if value is None:
        return ""
    if isinstance(value, dict):
        # Frequently extraction stores values under {"value": actual_value, ...}
        # Prefer the nested "value" entry when available.
        nested_value = value.get("value")
        if nested_value is not None:
            return format_value_for_pdf(field_path, nested_value)
        # Some fields might be stored as {"text": "..."} or similar
        nested_text = value.get("text")
        if nested_text is not None:
            return format_value_for_pdf(field_path, nested_text)
        # Fall back to empty string to avoid writing raw dict representations
        return ""
    # Dates: convert to MM/DD/YYYY if possible
    try:
        from datetime import date, datetime

        if isinstance(value, (date, datetime)):
            return value.strftime("%m/%d/%Y")
    except Exception:
        pass

    # Enums: store their value
    try:
        if hasattr(value, "value"):
            return str(getattr(value, "value"))
    except Exception:
        pass

    return str(value)






