"""
Multi-Form PDF Service

Handles generation of multiple ACORD forms:
- ACORD 125: Commercial Insurance Application
- ACORD 126: Commercial General Liability Section  
- ACORD 127: Commercial Auto Section
- ACORD 130: Workers Compensation Application
- ACORD 140: Property Section
"""

from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
import os
import logging
from enum import Enum

import pikepdf
from PyPDF2 import PdfReader

from app.config import settings
from app.services.s3_service import s3_service

logger = logging.getLogger(__name__)


class ACORDFormType(str, Enum):
    """Supported ACORD form types"""
    ACORD_125 = "ACORD_125"
    ACORD_126 = "ACORD_126"
    ACORD_127 = "ACORD_127"
    ACORD_130 = "ACORD_130"
    ACORD_140 = "ACORD_140"


# Template paths
FORM_TEMPLATES = {
    ACORDFormType.ACORD_125: "ACORD_125_fillable.pdf",
    ACORDFormType.ACORD_126: "ACORD_126_fillable.pdf",
    ACORDFormType.ACORD_127: "Acord_127_fillable.pdf",
    ACORDFormType.ACORD_130: "ACORD_130_fillable.pdf",
    ACORDFormType.ACORD_140: "ACORD_140_fillable.pdf",
}

# Form display names
FORM_DISPLAY_NAMES = {
    ACORDFormType.ACORD_125: "Commercial Insurance Application",
    ACORDFormType.ACORD_126: "Commercial General Liability Section",
    ACORDFormType.ACORD_127: "Commercial Auto Section",
    ACORDFormType.ACORD_130: "Workers Compensation Application",
    ACORDFormType.ACORD_140: "Property Section",
}


class MultiFormPDFService:
    """Service for generating multiple ACORD forms"""
    
    def __init__(self):
        self.template_base_path = getattr(settings, 'ACORD_TEMPLATES_PATH', 
            os.path.join(os.path.dirname(__file__), '../../static/acord-templates'))
        
        # Also check frontend public path
        if not os.path.exists(self.template_base_path):
            self.template_base_path = os.path.join(
                os.path.dirname(__file__), 
                '../../../frontend/public/acord-templates'
            )
    
    def get_template_path(self, form_type: ACORDFormType) -> str:
        """Get the template path for a form type"""
        template_name = FORM_TEMPLATES.get(form_type)
        if not template_name:
            raise ValueError(f"Unknown form type: {form_type}")
        
        # Try multiple paths
        paths_to_try = [
            os.path.join(self.template_base_path, template_name),
            os.path.join(settings.ACORD125_TEMPLATE_PATH.rsplit('/', 1)[0], template_name),
            f"/app/static/acord-templates/{template_name}",
            f"frontend/public/acord-templates/{template_name}",
        ]
        
        for path in paths_to_try:
            if os.path.isfile(path):
                return path
        
        raise FileNotFoundError(
            f"Template not found for {form_type}. Tried: {paths_to_try}"
        )
    
    def list_available_forms(self) -> List[Dict[str, str]]:
        """List all available ACORD forms"""
        available = []
        for form_type in ACORDFormType:
            try:
                path = self.get_template_path(form_type)
                available.append({
                    "form_type": form_type.value,
                    "display_name": FORM_DISPLAY_NAMES.get(form_type, form_type.value),
                    "template_exists": os.path.isfile(path),
                })
            except FileNotFoundError:
                available.append({
                    "form_type": form_type.value,
                    "display_name": FORM_DISPLAY_NAMES.get(form_type, form_type.value),
                    "template_exists": False,
                })
        return available
    
    def get_pdf_field_names(self, form_type: ACORDFormType) -> List[str]:
        """Get all field names from a PDF template (useful for mapping)"""
        template_path = self.get_template_path(form_type)
        try:
            reader = PdfReader(template_path)
            fields = reader.get_fields()
            if not fields:
                return []
            return list(fields.keys())
        except Exception as e:
            logger.error(f"Failed to get field names from {form_type}: {e}")
            return []
    
    def fill_form(
        self,
        form_type: ACORDFormType,
        data: Dict[str, Any],
        field_mapping: Optional[Dict[str, str]] = None
    ) -> bytes:
        """
        Fill an ACORD form with the provided data.
        
        Args:
            form_type: The type of ACORD form to fill
            data: Dictionary of data to fill
            field_mapping: Optional custom field mapping (schema_path -> pdf_field_name)
            
        Returns:
            Bytes of the filled PDF
        """
        template_path = self.get_template_path(form_type)
        
        # Get default mapping if not provided
        if field_mapping is None:
            field_mapping = self._get_default_field_mapping(form_type)
        
        # Flatten nested data to match field paths
        flattened_data = self._flatten_data(data)
        
        # Load PDF with pikepdf
        pdf = pikepdf.Pdf.open(template_path)
        
        # Get all PDF fields
        all_pdf_fields = self._collect_pdf_fields(pdf)
        logger.info(f"Found {len(all_pdf_fields)} fields in {form_type.value}")
        
        # Set NeedAppearances
        try:
            if '/AcroForm' in pdf.Root:
                pdf.Root['/AcroForm']['/NeedAppearances'] = pikepdf.Boolean(True)
        except Exception:
            pass
        
        # Fill fields
        updated_count = 0
        for schema_path, pdf_field_name in field_mapping.items():
            value = flattened_data.get(schema_path)
            if value is None or value == "":
                continue
            
            formatted_value = self._format_value(value)
            
            if pdf_field_name in all_pdf_fields:
                field_obj = all_pdf_fields[pdf_field_name]
                try:
                    field_obj['/V'] = pikepdf.String(str(formatted_value))
                    updated_count += 1
                    logger.debug(f"Set {pdf_field_name} = {formatted_value[:50] if len(str(formatted_value)) > 50 else formatted_value}")
                except Exception as e:
                    logger.warning(f"Failed to set field {pdf_field_name}: {e}")
        
        logger.info(f"Filled {updated_count} fields in {form_type.value}")
        
        # Write to bytes
        output = BytesIO()
        pdf.save(output)
        output.seek(0)
        return output.getvalue()
    
    def fill_multiple_forms(
        self,
        forms_data: List[Tuple[ACORDFormType, Dict[str, Any]]]
    ) -> Dict[str, bytes]:
        """
        Fill multiple ACORD forms.
        
        Args:
            forms_data: List of tuples (form_type, data_dict)
            
        Returns:
            Dictionary mapping form_type to filled PDF bytes
        """
        results = {}
        for form_type, data in forms_data:
            try:
                pdf_bytes = self.fill_form(form_type, data)
                results[form_type.value] = pdf_bytes
            except Exception as e:
                logger.error(f"Failed to fill {form_type.value}: {e}")
                results[form_type.value] = None
        return results
    
    def save_to_s3(
        self,
        user_id: str,
        submission_id: str,
        form_type: ACORDFormType,
        pdf_bytes: bytes
    ) -> Tuple[str, str]:
        """
        Save filled PDF to S3.
        
        Returns:
            Tuple of (s3_key, presigned_url)
        """
        key = f"submissions/{user_id}/{submission_id}/{form_type.value.lower()}-filled.pdf"
        
        if s3_service.s3_client is None:
            return key, f"/dev/null/{key}"
        
        s3_service.s3_client.put_object(
            Bucket=s3_service.bucket_name,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )
        
        url = s3_service.generate_presigned_download_url(key)
        return key, url
    
    def _collect_pdf_fields(self, pdf: pikepdf.Pdf) -> Dict[str, Any]:
        """Collect all PDF form fields"""
        fields = {}
        
        def collect(obj, parent_path=""):
            try:
                if isinstance(obj, pikepdf.Dictionary):
                    if '/T' in obj:
                        name_obj = obj['/T']
                        if isinstance(name_obj, pikepdf.Name):
                            obj_name = str(name_obj)[1:]
                        else:
                            obj_name = str(name_obj)
                        
                        full_path = f"{parent_path}.{obj_name}" if parent_path else obj_name
                        fields[full_path] = obj
                        fields[obj_name] = obj
                        
                        if '/Kids' in obj:
                            for kid in obj['/Kids']:
                                collect(kid, full_path)
                    elif '/Kids' in obj:
                        for kid in obj['/Kids']:
                            collect(kid, parent_path)
            except Exception as e:
                logger.debug(f"Error collecting field: {e}")
        
        if '/AcroForm' in pdf.Root and '/Fields' in pdf.Root['/AcroForm']:
            for field in pdf.Root['/AcroForm']['/Fields']:
                collect(field)
        
        return fields
    
    def _flatten_data(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dictionary to dot-notation keys"""
        result = {}
        
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Check if it's a wrapped value
                if "value" in value and "confidence" in value:
                    result[full_key] = value.get("value")
                else:
                    result.update(self._flatten_data(value, full_key))
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        result.update(self._flatten_data(item, f"{full_key}[{idx}]"))
                    else:
                        result[f"{full_key}[{idx}]"] = item
            else:
                result[full_key] = value
        
        return result
    
    def _format_value(self, value: Any) -> str:
        """Format a value for PDF field"""
        if value is None:
            return ""
        
        # Handle wrapped values
        if isinstance(value, dict) and "value" in value:
            value = value.get("value")
        
        # Handle dates
        try:
            from datetime import date, datetime
            if isinstance(value, (date, datetime)):
                return value.strftime("%m/%d/%Y")
        except Exception:
            pass
        
        # Handle enums
        if hasattr(value, "value"):
            return str(value.value)
        
        # Handle decimals
        try:
            from decimal import Decimal
            if isinstance(value, Decimal):
                return str(value)
        except Exception:
            pass
        
        return str(value)
    
    def _get_default_field_mapping(self, form_type: ACORDFormType) -> Dict[str, str]:
        """Get default field mapping for a form type"""
        
        if form_type == ACORDFormType.ACORD_125:
            # Import existing ACORD 125 mapping
            from app.core.pdf_field_mapping import CRITICAL_FIELD_MAPPING
            return CRITICAL_FIELD_MAPPING
        
        elif form_type == ACORDFormType.ACORD_126:
            return self._get_acord126_mapping()
        
        elif form_type == ACORDFormType.ACORD_130:
            return self._get_acord130_mapping()
        
        elif form_type == ACORDFormType.ACORD_127:
            return self._get_acord127_mapping()
        
        elif form_type == ACORDFormType.ACORD_140:
            return self._get_acord140_mapping()
        
        return {}
    
    def _get_acord126_mapping(self) -> Dict[str, str]:
        """Field mapping for ACORD 126"""
        # These are common field patterns - actual field names need to be verified
        # against the specific PDF template
        return {
            # Header
            "named_insured": "F[0].P1[0].NamedInsured_FullName[0]",
            "policy_number": "F[0].P1[0].Policy_PolicyNumber[0]",
            "effective_date": "F[0].P1[0].Policy_EffectiveDate[0]",
            
            # Limits
            "limits.general_aggregate": "F[0].P1[0].GL_GeneralAggregate[0]",
            "limits.products_co_aggregate": "F[0].P1[0].GL_ProductsCOAggregate[0]",
            "limits.personal_advertising_injury": "F[0].P1[0].GL_PersonalAdvertisingInjury[0]",
            "limits.each_occurrence": "F[0].P1[0].GL_EachOccurrence[0]",
            "limits.damage_to_rented_premises": "F[0].P1[0].GL_DamageToRentedPremises[0]",
            "limits.medical_expense": "F[0].P1[0].GL_MedicalExpense[0]",
            
            # Classifications
            "classifications[0].class_code": "F[0].P1[0].GL_ClassCode_A[0]",
            "classifications[0].classification_description": "F[0].P1[0].GL_Classification_A[0]",
            "classifications[0].premium_basis": "F[0].P1[0].GL_PremiumBasis_A[0]",
            "classifications[0].exposure": "F[0].P1[0].GL_Exposure_A[0]",
            "classifications[0].premium": "F[0].P1[0].GL_Premium_A[0]",
            
            # Premium
            "total_premium": "F[0].P1[0].GL_TotalPremium[0]",
        }
    
    def _get_acord130_mapping(self) -> Dict[str, str]:
        """Field mapping for ACORD 130"""
        return {
            # Header
            "named_insured": "F[0].P1[0].NamedInsured_FullName[0]",
            "fein": "F[0].P1[0].NamedInsured_FEIN[0]",
            "policy_number": "F[0].P1[0].Policy_PolicyNumber[0]",
            "effective_date": "F[0].P1[0].Policy_EffectiveDate[0]",
            "expiration_date": "F[0].P1[0].Policy_ExpirationDate[0]",
            
            # Experience Mod
            "experience_mod.mod_rate": "F[0].P1[0].WC_ExperienceMod[0]",
            "experience_mod.effective_date": "F[0].P1[0].WC_ModEffectiveDate[0]",
            
            # Classifications
            "classifications[0].state": "F[0].P1[0].WC_State_A[0]",
            "classifications[0].class_code": "F[0].P1[0].WC_ClassCode_A[0]",
            "classifications[0].classification_description": "F[0].P1[0].WC_Classification_A[0]",
            "classifications[0].number_of_employees": "F[0].P1[0].WC_Employees_A[0]",
            "classifications[0].annual_remuneration": "F[0].P1[0].WC_Payroll_A[0]",
            "classifications[0].rate": "F[0].P1[0].WC_Rate_A[0]",
            "classifications[0].estimated_premium": "F[0].P1[0].WC_Premium_A[0]",
            
            "classifications[1].state": "F[0].P1[0].WC_State_B[0]",
            "classifications[1].class_code": "F[0].P1[0].WC_ClassCode_B[0]",
            "classifications[1].classification_description": "F[0].P1[0].WC_Classification_B[0]",
            "classifications[1].number_of_employees": "F[0].P1[0].WC_Employees_B[0]",
            "classifications[1].annual_remuneration": "F[0].P1[0].WC_Payroll_B[0]",
            
            # Owners/Officers
            "owners_officers[0].name": "F[0].P1[0].WC_OwnerOfficer_Name_A[0]",
            "owners_officers[0].title": "F[0].P1[0].WC_OwnerOfficer_Title_A[0]",
            "owners_officers[0].duties": "F[0].P1[0].WC_OwnerOfficer_Duties_A[0]",
            "owners_officers[0].annual_remuneration": "F[0].P1[0].WC_OwnerOfficer_Remuneration_A[0]",
            
            # Totals
            "total_employees": "F[0].P1[0].WC_TotalEmployees[0]",
            "total_estimated_annual_premium": "F[0].P1[0].WC_TotalPremium[0]",
        }
    
    def _get_acord127_mapping(self) -> Dict[str, str]:
        """Field mapping for ACORD 127 (Commercial Auto) - Based on actual PDF field names"""
        mapping = {
            # Header (Page 1)
            "named_insured": "F[0].P1[0].NamedInsured_FullName_A[0]",
            "policy_number": "F[0].P1[0].Policy_PolicyNumberIdentifier_A[0]",
            "effective_date": "F[0].P1[0].Policy_EffectiveDate_A[0]",
            "producer_name": "F[0].P1[0].Producer_FullName_A[0]",
            "producer_customer_id": "F[0].P1[0].Producer_CustomerIdentifier_A[0]",
            "insurer_name": "F[0].P1[0].Insurer_FullName_A[0]",
            "insurer_naic": "F[0].P1[0].Insurer_NAICCode_A[0]",
            "form_date": "F[0].P1[0].Form_CompletionDate_A[0]",
            
            # Additional Interest (Page 2)
            "additional_interest[0].name": "F[0].P2[0].AdditionalInterest_FullName_A[0]",
            "additional_interest[0].address": "F[0].P2[0].AdditionalInterest_MailingAddress_LineOne_A[0]",
            "additional_interest[0].city": "F[0].P2[0].AdditionalInterest_MailingAddress_CityName_A[0]",
            "additional_interest[0].state": "F[0].P2[0].AdditionalInterest_MailingAddress_StateOrProvinceCode_A[0]",
            "additional_interest[0].zip": "F[0].P2[0].AdditionalInterest_MailingAddress_PostalCode_A[0]",
            
            # Accident/Conviction History (Page 2)
            "accident_history[0].driver_id": "F[0].P2[0].AccidentConviction_DriverProducerIdentifier_A[0]",
            "accident_history[0].date": "F[0].P2[0].AccidentConviction_IncidentDate_A[0]",
            "accident_history[0].description": "F[0].P2[0].AccidentConviction_IncidentDescription_A[0]",
            "accident_history[0].location": "F[0].P2[0].AccidentConviction_PlaceOfIncident_A[0]",
            
            # Remarks
            "remarks": "F[0].P2[0].CommercialVehicleLineOfBusiness_RemarkText_A[0]",
            "remarks_continued": "F[0].P2[0].CommercialVehicleLineOfBusiness_RemarkText_B[0]",
            
            # Maximum Exposure
            "max_exposure_all_vehicles": "F[0].P2[0].CommercialVehicleLineOfBusiness_MaximumExposureAllVehiclesAmount_A[0]",
            
            # Signature (Page 3)
            "signature_date": "F[0].P3[0].NamedInsured_SignatureDate_A[0]",
            "producer_rep_name": "F[0].P3[0].Producer_AuthorizedRepresentative_FullName_A[0]",
            "producer_license": "F[0].P3[0].Producer_StateLicenseIdentifier_A[0]",
            "producer_national_id": "F[0].P3[0].Producer_NationalIdentifier_A[0]",
        }
        
        # Driver Schedule - Support up to 12 drivers (A through L)
        driver_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        for idx, letter in enumerate(driver_letters):
            prefix = f"driver_schedule[{idx}]"
            mapping.update({
                f"{prefix}.first_name": f"F[0].P1[0].Driver_GivenName_{letter}[0]",
                f"{prefix}.last_name": f"F[0].P1[0].Driver_Surname_{letter}[0]",
                f"{prefix}.middle_initial": f"F[0].P1[0].Driver_OtherGivenNameInitial_{letter}[0]",
                f"{prefix}.date_of_birth": f"F[0].P1[0].Driver_BirthDate_{letter}[0]",
                f"{prefix}.gender": f"F[0].P1[0].Driver_GenderCode_{letter}[0]",
                f"{prefix}.marital_status": f"F[0].P1[0].Driver_MaritalStatusCode_{letter}[0]",
                f"{prefix}.license_number": f"F[0].P1[0].Driver_LicenseNumberIdentifier_{letter}[0]",
                f"{prefix}.license_state": f"F[0].P1[0].Driver_LicensedStateOrProvinceCode_{letter}[0]",
                f"{prefix}.license_year": f"F[0].P1[0].Driver_LicensedYear_{letter}[0]",
                f"{prefix}.years_experience": f"F[0].P1[0].Driver_ExperienceYearCount_{letter}[0]",
                f"{prefix}.date_hired": f"F[0].P1[0].Driver_HiredDate_{letter}[0]",
                f"{prefix}.ssn": f"F[0].P1[0].Driver_TaxIdentifier_{letter}[0]",
                f"{prefix}.address": f"F[0].P1[0].Driver_MailingAddress_LineOne_{letter}[0]",
                f"{prefix}.city": f"F[0].P1[0].Driver_MailingAddress_CityName_{letter}[0]",
                f"{prefix}.state": f"F[0].P1[0].Driver_MailingAddress_StateOrProvinceCode_{letter}[0]",
                f"{prefix}.zip": f"F[0].P1[0].Driver_MailingAddress_PostalCode_{letter}[0]",
            })
        
        # Vehicle Schedule - Support up to 8 vehicles (A through H on Page 3)
        vehicle_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for idx, letter in enumerate(vehicle_letters):
            prefix = f"vehicle_schedule[{idx}]"
            mapping.update({
                f"{prefix}.year": f"F[0].P3[0].Vehicle_ModelYear_{letter}[0]",
                f"{prefix}.make": f"F[0].P3[0].Vehicle_ManufacturersName_{letter}[0]",
                f"{prefix}.model": f"F[0].P3[0].Vehicle_ModelName_{letter}[0]",
                f"{prefix}.vin": f"F[0].P3[0].Vehicle_VINIdentifier_{letter}[0]",
                f"{prefix}.body_type": f"F[0].P3[0].Vehicle_BodyCode_{letter}[0]",
                f"{prefix}.gvw": f"F[0].P3[0].Vehicle_GrossVehicleWeight_{letter}[0]",
                f"{prefix}.cost_new": f"F[0].P3[0].Vehicle_CostNewAmount_{letter}[0]",
                f"{prefix}.radius": f"F[0].P3[0].Vehicle_RadiusOfUse_{letter}[0]",
                f"{prefix}.farthest_zone": f"F[0].P3[0].Vehicle_FarthestZoneCode_{letter}[0]",
                f"{prefix}.seating_capacity": f"F[0].P3[0].Vehicle_SeatingCapacityCount_{letter}[0]",
                f"{prefix}.registration_state": f"F[0].P3[0].Vehicle_Registration_StateOrProvinceCode_{letter}[0]",
                f"{prefix}.rating_territory": f"F[0].P3[0].Vehicle_RatingTerritoryCode_{letter}[0]",
                f"{prefix}.class_code": f"F[0].P3[0].Vehicle_RateClassCode_{letter}[0]",
                f"{prefix}.total_premium": f"F[0].P3[0].Vehicle_TotalPremiumAmount_{letter}[0]",
                # Coverages
                f"{prefix}.liability": f"F[0].P3[0].Vehicle_Coverage_LiabilityIndicator_{letter}[0]",
                f"{prefix}.comprehensive": f"F[0].P3[0].Vehicle_Coverage_ComprehensiveIndicator_{letter}[0]",
                f"{prefix}.collision": f"F[0].P3[0].Vehicle_Coverage_CollisionIndicator_{letter}[0]",
                f"{prefix}.medical_payments": f"F[0].P3[0].Vehicle_Coverage_MedicalPaymentsIndicator_{letter}[0]",
                f"{prefix}.uninsured_motorist": f"F[0].P3[0].Vehicle_Coverage_UninsuredMotoristsIndicator_{letter}[0]",
                f"{prefix}.underinsured_motorist": f"F[0].P3[0].Vehicle_Coverage_UnderinsuredMotoristsIndicator_{letter}[0]",
                f"{prefix}.comp_deductible": f"F[0].P3[0].Vehicle_Coverage_ComprehensiveOrSpecifiedCauseOfLossDeductibleAmount_{letter}[0]",
                f"{prefix}.collision_deductible": f"F[0].P3[0].Vehicle_Collision_DeductibleAmount_{letter}[0]",
                f"{prefix}.stated_amount": f"F[0].P3[0].Vehicle_Coverage_AgreedOrStatedAmount_{letter}[0]",
                # Garage Location
                f"{prefix}.garage_address": f"F[0].P3[0].Vehicle_PhysicalAddress_LineOne_{letter}[0]",
                f"{prefix}.garage_city": f"F[0].P3[0].Vehicle_PhysicalAddress_CityName_{letter}[0]",
                f"{prefix}.garage_state": f"F[0].P3[0].Vehicle_PhysicalAddress_StateOrProvinceCode_{letter}[0]",
                f"{prefix}.garage_zip": f"F[0].P3[0].Vehicle_PhysicalAddress_PostalCode_{letter}[0]",
                f"{prefix}.garage_county": f"F[0].P3[0].Vehicle_PhysicalAddress_CountyName_{letter}[0]",
            })
        
        return mapping
    
    def _get_acord140_mapping(self) -> Dict[str, str]:
        """Field mapping for ACORD 140"""
        return {
            # Header
            "named_insured": "F[0].P1[0].NamedInsured_FullName[0]",
            "policy_number": "F[0].P1[0].Policy_PolicyNumber[0]",
            "effective_date": "F[0].P1[0].Policy_EffectiveDate[0]",
            
            # Building 1
            "buildings[0].street_address": "F[0].P1[0].Property_Address_A[0]",
            "buildings[0].city": "F[0].P1[0].Property_City_A[0]",
            "buildings[0].state": "F[0].P1[0].Property_State_A[0]",
            "buildings[0].zip_code": "F[0].P1[0].Property_Zip_A[0]",
            "buildings[0].construction_type": "F[0].P1[0].Property_Construction_A[0]",
            "buildings[0].year_built": "F[0].P1[0].Property_YearBuilt_A[0]",
            "buildings[0].number_of_stories": "F[0].P1[0].Property_Stories_A[0]",
            "buildings[0].total_area_sq_ft": "F[0].P1[0].Property_SqFt_A[0]",
            
            # Coverage 1
            "coverages[0].building_limit": "F[0].P1[0].Property_BuildingLimit_A[0]",
            "coverages[0].bpp_limit": "F[0].P1[0].Property_BPPLimit_A[0]",
            "coverages[0].business_income_limit": "F[0].P1[0].Property_BILimit_A[0]",
            "coverages[0].deductible": "F[0].P1[0].Property_Deductible_A[0]",
            "coverages[0].cause_of_loss": "F[0].P1[0].Property_CauseOfLoss_A[0]",
            
            # Building 2
            "buildings[1].street_address": "F[0].P1[0].Property_Address_B[0]",
            "buildings[1].city": "F[0].P1[0].Property_City_B[0]",
            "buildings[1].state": "F[0].P1[0].Property_State_B[0]",
            "buildings[1].zip_code": "F[0].P1[0].Property_Zip_B[0]",
            
            # Totals
            "total_property_premium": "F[0].P1[0].Property_TotalPremium[0]",
        }


# Global service instance
multi_form_pdf_service = MultiFormPDFService()








