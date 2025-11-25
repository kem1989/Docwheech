"""
PDF generation service for filling ACORD 125 form fields.
Uses pikepdf to reliably fill AcroForm fields and produce a valid PDF.
"""

from io import BytesIO
from typing import Dict, Any, Tuple, List, Optional
import os
import logging

import pikepdf
from PyPDF2 import PdfReader  # kept for field discovery when needed

from app.config import settings
from app.core.acord_schema import ACORD125Schema
from app.core.pdf_field_mapping import (
    CRITICAL_FIELD_MAPPING,
    LINE_OF_BUSINESS_CHECKBOX_MAPPING,
    NATURE_OF_BUSINESS_TYPE_CHECKBOX_MAPPING,
    PREMISES_INTEREST_CHECKBOX_MAPPING,
    BUSINESS_STRUCTURE_CHECKBOX_MAPPING,
    TRANSACTION_STATUS_NORMALIZATION,
    TRANSACTION_STATUS_CHECKBOX_MAPPING,
    GENERAL_QUESTIONS_MAPPING,
    format_value_for_pdf,
)
PRIOR_CARRIER_SLOT_LETTERS = {0: "A", 1: "B", 2: "C"}
PRIOR_CARRIER_SLOT_PAGES = {0: "P3", 1: "P4", 2: "P4"}
PRIOR_CARRIER_CATEGORY_BASE = {
    "GENERAL_LIABILITY": "GeneralLiability",
    "AUTOMOBILE": "Automobile",
    "PROPERTY": "Property",
    "OTHER": "OtherLine",
}
PRIOR_CARRIER_FIELD_SUFFIXES = {
    "carrier_name": "InsurerFullName",
    "policy_number": "PolicyNumberIdentifier",
    "premium": "TotalPremiumAmount",
    "effective_date": "EffectiveDate",
    "expiration_date": "ExpirationDate",
}

from app.services.s3_service import s3_service

LOSS_HISTORY_FIELD_SUFFIXES = ["A", "B", "C"]

logger = logging.getLogger(__name__)


def _flatten_schema_paths(acord: ACORD125Schema) -> Dict[str, Any]:
    """Flatten selected schema paths used by CRITICAL_FIELD_MAPPING."""
    data = acord.to_dict()

    def get_path(path: str) -> Any:
        cur: Any = data
        segments = []
        # handle list index syntax like premises[0].city
        for token in path.split('.'):
            if '[' in token and token.endswith(']'):
                name, idx_str = token[:-1].split('[')
                cur = cur.get(name) if isinstance(cur, dict) else None
                if cur is None or not isinstance(cur, list):
                    return None
                try:
                    idx = int(idx_str)
                except ValueError:
                    return None
                cur = cur[idx] if idx < len(cur) else None
            else:
                cur = cur.get(token) if isinstance(cur, dict) else None
            if cur is None:
                return None
            segments.append(token)
        return cur

    flattened: Dict[str, Any] = {}
    for schema_path in CRITICAL_FIELD_MAPPING.keys():
        flattened[schema_path] = get_path(schema_path)
    return flattened


def generate_filled_pdf_bytes(acord: ACORD125Schema, general_questions: Optional[List[Dict[str, Any]]] = None) -> bytes:
    """Fill ACORD 125 PDF with mapped fields and return bytes of the filled PDF."""
    template_path = settings.ACORD125_TEMPLATE_PATH
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")

    # Prepare field values from schema
    flattened = _flatten_schema_paths(acord)
    field_values: Dict[str, Any] = {}
    checkbox_field_values: Dict[str, bool] = {}
    transaction_type_value: Any = None
    lines_of_business_value: Any = None
    nature_of_business_types: Any = None
    premises_interest_values: Dict[int, Any] = {}
    business_structure_value: Optional[str] = None

    for schema_path, pdf_field in CRITICAL_FIELD_MAPPING.items():
        value = flattened.get(schema_path)
        formatted_value = format_value_for_pdf(schema_path, value)
        if schema_path == "transaction_status.type":
            if formatted_value:
                transaction_type_value = formatted_value
            continue
        if schema_path == "lines_of_business":
            if value:
                lines_of_business_value = value
            continue
        if schema_path == "nature_of_business.business_type":
            if value:
                nature_of_business_types = value
            continue
        if schema_path == "first_named_insured.business_structure":
            if formatted_value:
                business_structure_value = formatted_value
            continue
        if schema_path.startswith("premises[") and schema_path.endswith(".interest"):
            try:
                premises_index = int(schema_path.split("premises[", 1)[1].split("]", 1)[0])
            except (IndexError, ValueError):
                premises_index = None
            if premises_index is not None and formatted_value:
                premises_interest_values[premises_index] = formatted_value
            continue
        if formatted_value:
            field_values[pdf_field] = formatted_value

    logger.warning(f"transaction_status.type raw value from schema: {flattened.get('transaction_status.type')!r}")
    logger.warning(f"transaction_status.type formatted value: {transaction_type_value!r}")

    if transaction_type_value:
        normalized_transaction_value = str(transaction_type_value).strip().upper()
        normalized_transaction_value = TRANSACTION_STATUS_NORMALIZATION.get(
            normalized_transaction_value, normalized_transaction_value
        )
        logger.warning(f"transaction_status.type normalized value: {normalized_transaction_value!r}")
        if normalized_transaction_value in TRANSACTION_STATUS_CHECKBOX_MAPPING:
            target_field = TRANSACTION_STATUS_CHECKBOX_MAPPING[normalized_transaction_value]
            logger.warning(
                f"transaction_status.type checkbox target field: {target_field} "
                f"(all choices: {TRANSACTION_STATUS_CHECKBOX_MAPPING})"
            )
            for status_value, checkbox_field in TRANSACTION_STATUS_CHECKBOX_MAPPING.items():
                checkbox_field_values[checkbox_field] = checkbox_field == target_field
            logger.warning(f"Prepared transaction_status checkbox values: {checkbox_field_values}")
        else:
            logger.warning(
                f"Unknown transaction status '{transaction_type_value}' (normalized to '{normalized_transaction_value}') encountered; skipping checkbox fill."
            )

    if isinstance(lines_of_business_value, list):
        for enum_value, checkbox_field in LINE_OF_BUSINESS_CHECKBOX_MAPPING.items():
            is_checked = any(
                isinstance(entry, dict)
                and entry.get("line") == enum_value
                and entry.get("selected") in (True, "true", "True", "TRUE", 1)
                for entry in lines_of_business_value
            )
            checkbox_field_values[checkbox_field] = is_checked
    elif lines_of_business_value is not None:
        logger.warning("lines_of_business value is not a list; skipping checkbox fill.")

    if isinstance(nature_of_business_types, list):
        normalized_types = {
            str(item).strip().lower()
            for item in nature_of_business_types
            if item is not None
        }
        for type_key, checkbox_field in NATURE_OF_BUSINESS_TYPE_CHECKBOX_MAPPING.items():
            checkbox_field_values[checkbox_field] = type_key.lower() in normalized_types
        logger.warning(
            f"nature_of_business.business_type values: {nature_of_business_types} "
            f"=> normalized {normalized_types}"
        )
    elif isinstance(nature_of_business_types, str):
        normalized = nature_of_business_types.strip().lower()
        for type_key, checkbox_field in NATURE_OF_BUSINESS_TYPE_CHECKBOX_MAPPING.items():
            checkbox_field_values[checkbox_field] = type_key.lower() == normalized
        logger.warning(
            f"nature_of_business.business_type single value: {nature_of_business_types} "
            f"=> normalized {normalized}"
        )
    elif nature_of_business_types:
        logger.warning("nature_of_business.business_type format not recognized; skipping checkbox fill.")

    if business_structure_value:
        normalized_structure = str(business_structure_value).strip().upper()
        target_field = BUSINESS_STRUCTURE_CHECKBOX_MAPPING.get(normalized_structure)
        if target_field:
            for option_value, checkbox_field in BUSINESS_STRUCTURE_CHECKBOX_MAPPING.items():
                checkbox_field_values[checkbox_field] = checkbox_field == target_field
            logger.warning(
                f"first_named_insured.business_structure '{business_structure_value}' normalized to "
                f"'{normalized_structure}' mapped to checkbox '{target_field}'"
            )
        else:
            logger.warning(
                f"Unknown business structure '{business_structure_value}' (normalized '{normalized_structure}')"
            )

    for premises_index, interest_value in premises_interest_values.items():
        normalized_interest = str(interest_value).strip().lower()
        interest_mapping = PREMISES_INTEREST_CHECKBOX_MAPPING.get(premises_index)
        if not interest_mapping:
            logger.warning(
                f"No checkbox mapping configured for premises index {premises_index}; skipping interest checkbox fill."
            )
            continue
        target_field = interest_mapping.get(normalized_interest)
        if target_field:
            for option, checkbox_field in interest_mapping.items():
                checkbox_field_values[checkbox_field] = checkbox_field == target_field
            logger.warning(
                f"premises[{premises_index}].interest value '{interest_value}' normalized to '{normalized_interest}' "
                f"mapped to checkbox '{target_field}'"
            )
        else:
            logger.warning(
                f"Unknown premises[{premises_index}] interest '{interest_value}' (normalized '{normalized_interest}')"
            )

    prior_carriers = list(acord.prior_carriers or [])

    def _prior_field_name(slot_index: int, category_base: str, suffix_key: str) -> Optional[str]:
        page = PRIOR_CARRIER_SLOT_PAGES.get(slot_index)
        letter = PRIOR_CARRIER_SLOT_LETTERS.get(slot_index)
        suffix = PRIOR_CARRIER_FIELD_SUFFIXES.get(suffix_key)
        if not page or not letter or not suffix:
            return None
        return f"F[0].{page}[0].PriorCoverage_{category_base}_{suffix}_{letter}[0]"

    for idx, carrier in enumerate(prior_carriers[:3]):
        category_value = getattr(carrier, "category", None)
        if category_value is None:
            logger.warning(f"prior_carriers[{idx}] missing category; skipping.")
            continue
        category_key = str(getattr(category_value, "value", category_value)).upper()
        category_base = PRIOR_CARRIER_CATEGORY_BASE.get(category_key)
        if not category_base:
            logger.warning(f"prior_carriers[{idx}] category '{category_key}' not supported for PDF mapping.")
            continue

        field_map = {
            "carrier_name": getattr(carrier, "carrier_name", None),
            "policy_number": getattr(carrier, "policy_number", None),
            "premium": getattr(carrier, "premium", None),
            "effective_date": getattr(carrier, "effective_date", None),
            "expiration_date": getattr(carrier, "expiration_date", None),
        }

        for key, raw_value in field_map.items():
            if raw_value is None:
                continue
            if isinstance(raw_value, str) and not raw_value.strip():
                continue
            formatted = format_value_for_pdf(f"prior_carriers.{key}", raw_value)
            if not formatted:
                continue
            field_name = _prior_field_name(idx, category_base, key)
            if not field_name:
                logger.warning(f"prior_carriers[{idx}] field mapping missing for key '{key}'.")
                continue
            field_values[field_name] = formatted
            logger.info(f"Mapped prior_carriers[{idx}] {key} -> '{field_name}' = '{formatted}'")

    loss_history = acord.loss_history
    if loss_history and loss_history.losses:
        for idx, loss in enumerate(loss_history.losses[:3]):
            slot_suffix = LOSS_HISTORY_FIELD_SUFFIXES[idx]
            date_of_loss = getattr(loss, "date_of_loss", None)
            description = getattr(loss, "description_of_occurrence", None)
            amount_paid = getattr(loss, "amount_paid", None)

            if date_of_loss:
                field_name = f"F[0].P4[0].LossHistory_OccurrenceDate_{slot_suffix}[0]"
                formatted = format_value_for_pdf(f"loss_history.losses[{idx}].date_of_loss", date_of_loss)
                if formatted:
                    field_values[field_name] = formatted
                    logger.info(f"Mapped loss[{idx}] date_of_loss -> '{field_name}' = '{formatted}'")

            if description:
                field_name = f"F[0].P4[0].LossHistory_OccurrenceDescription_{slot_suffix}[0]"
                formatted = format_value_for_pdf(
                    f"loss_history.losses[{idx}].description_of_occurrence", description
                )
                if formatted:
                    field_values[field_name] = formatted
                    logger.info(f"Mapped loss[{idx}] description -> '{field_name}' = '{formatted}'")

            if amount_paid not in (None, ""):
                field_name = f"F[0].P4[0].LossHistory_PaidAmount_{slot_suffix}[0]"
                formatted = format_value_for_pdf(f"loss_history.losses[{idx}].amount_paid", amount_paid)
                if formatted:
                    field_values[field_name] = formatted
                    logger.info(f"Mapped loss[{idx}] amount_paid -> '{field_name}' = '{formatted}'")

    # Process general questions if provided
    if general_questions:
        logger.info(f"Processing {len(general_questions)} general questions")
        for question in general_questions:
            question_id = question.get("id")
            answer = question.get("answer")
            details = question.get("details")
            
            if question_id not in GENERAL_QUESTIONS_MAPPING:
                logger.warning(f"Unknown general question ID: {question_id}")
                continue
            
            mapping = GENERAL_QUESTIONS_MAPPING[question_id]
            checkbox_field = mapping.get("checkbox")
            details_field = mapping.get("details")
            structured_detail_fields = mapping.get("detail_fields")
            
            # Fill with "Y" for Yes, "N" for No (not checkbox states)
            if checkbox_field and answer is not None:
                # Map True -> "Y", False -> "N"
                answer_value = "Y" if answer is True else "N"
                field_values[checkbox_field] = answer_value
                logger.info(f"Mapped general question '{question_id}' field '{checkbox_field}' = '{answer_value}'")
            
            # Fill structured detail fields if configured
            if (
                structured_detail_fields
                and isinstance(details, dict)
                and answer is True
            ):
                for detail_key, pdf_field in structured_detail_fields.items():
                    field_value = details.get(detail_key)
                    if field_value not in (None, ""):
                        formatted_detail = format_value_for_pdf(
                            f"general_questions.{question_id}.{detail_key}", field_value
                        )
                        if formatted_detail:
                            field_values[pdf_field] = formatted_detail
                            logger.info(
                                "Mapped general question '%s' structured detail '%s' -> '%s' = '%s'",
                                question_id,
                                detail_key,
                                pdf_field,
                                formatted_detail,
                            )

            # Fill single details text field if configured and answer is Yes
            if (
                details_field
                and answer is True
                and isinstance(details, str)
                and details
            ):
                formatted_details = format_value_for_pdf(f"general_questions.{question_id}.details", details)
                if formatted_details:
                    field_values[details_field] = formatted_details
                    logger.info(f"Mapped general question '{question_id}' details -> '{details_field}' = '{formatted_details[:50]}...'")

    logger.warning(
        f"Prepared {len(field_values)} text fields and {len(checkbox_field_values)} checkboxes to fill"
    )
    logger.warning(f"Field values: {field_values}")
    if checkbox_field_values:
        logger.warning(f"Checkbox values: {checkbox_field_values}")

    # Use PyPDF2 to get field names (we know this works), then pikepdf to fill them
    # First, get field names from PyPDF2
    reader = PdfReader(template_path)
    pdf2_fields = reader.get_fields() or {}
    logger.info(f"PyPDF2 found {len(pdf2_fields)} fields")
    
    # Build a mapping: field name -> field object in pikepdf
    # Load PDF with pikepdf (handles compressed streams well)
    pdf = pikepdf.Pdf.open(template_path)
    
    updated_count = 0
    field_name_to_obj = {}
    
    # Create mapping from PyPDF2 field names to pikepdf field objects
    # Build a flat list of all pikepdf field objects with their names
    all_pikepdf_fields = {}
    
    def collect_pikepdf_fields(obj, parent_path=""):
        """Collect all pikepdf field objects with their full paths"""
        try:
            if isinstance(obj, pikepdf.Dictionary):
                if '/T' in obj:
                    name_obj = obj['/T']
                    if isinstance(name_obj, pikepdf.Name):
                        obj_name = str(name_obj)[1:]  # Remove leading '/'
                    else:
                        obj_name = str(name_obj)
                    
                    # Build full path
                    if parent_path:
                        full_path = f"{parent_path}.{obj_name}"
                    else:
                        full_path = obj_name
                    
                    # Store both full path and short name
                    all_pikepdf_fields[full_path] = obj
                    all_pikepdf_fields[obj_name] = obj
                    
                    # Recurse into Kids
                    if '/Kids' in obj:
                        for kid in obj['/Kids']:
                            collect_pikepdf_fields(kid, full_path)
                elif '/Kids' in obj:
                    # No name but has Kids - recurse
                    for kid in obj['/Kids']:
                        collect_pikepdf_fields(kid, parent_path)
        except Exception as e:
            logger.debug(f"Error collecting pikepdf field: {str(e)}")
    
    # Collect all pikepdf field objects
    if '/AcroForm' in pdf.Root and '/Fields' in pdf.Root['/AcroForm']:
        for field in pdf.Root['/AcroForm']['/Fields']:
            collect_pikepdf_fields(field)
    
    logger.info(f"Collected {len(all_pikepdf_fields)} pikepdf field objects")
    
    # Now match PyPDF2 field names to pikepdf objects (1:1 mapping)
    for pdf2_field_name in pdf2_fields.keys():
        # Try exact match first
        if pdf2_field_name in all_pikepdf_fields:
            field_name_to_obj[pdf2_field_name] = all_pikepdf_fields[pdf2_field_name]
        else:
            # Try matching by last component (field name after last dot)
            if '.' in pdf2_field_name:
                base_name = pdf2_field_name.split('.')[-1]
                # Look for exact match of base name
                if base_name in all_pikepdf_fields:
                    field_name_to_obj[pdf2_field_name] = all_pikepdf_fields[base_name]
                else:
                    # Try partial match - find field where base name appears in pikepdf field name
                    for pikepdf_name, pikepdf_obj in all_pikepdf_fields.items():
                        if base_name == pikepdf_name or (base_name in pikepdf_name and pikepdf_name.endswith(base_name)):
                            field_name_to_obj[pdf2_field_name] = pikepdf_obj
                            break
    
    logger.info(f"Mapped {len(field_name_to_obj)} PyPDF2 field names to pikepdf objects")
    logger.info(f"Sample mapped fields: {list(field_name_to_obj.keys())[:10]}")
    
    # Set NeedAppearances
    try:
        pdf.Root['/AcroForm']['/NeedAppearances'] = pikepdf.Boolean(True)
    except:
        try:
            pdf.Root['/AcroForm']['/NeedAppearances'] = pikepdf.Name('/true')
        except:
            pass
    
    # Update fields using our mapping
    def _determine_checkbox_states(field_obj: pikepdf.Dictionary) -> Tuple[pikepdf.Name, pikepdf.Name]:
        """Return (on_state, off_state) names for a checkbox field."""
        off_state = pikepdf.Name('/Off')
        on_state: pikepdf.Name = pikepdf.Name('/Yes')
        try:
            ap_dict = field_obj.get('/AP')
            if isinstance(ap_dict, pikepdf.Dictionary):
                for state_name in ap_dict.keys():
                    if isinstance(state_name, pikepdf.Name) and state_name != off_state:
                        on_state = state_name
                        break
        except Exception as e:
            logger.debug(f"Could not determine checkbox on-state: {e}")
        return on_state, off_state

    def _set_checkbox(field_obj: pikepdf.Dictionary, is_checked: bool) -> None:
        on_state, off_state = _determine_checkbox_states(field_obj)
        selected_state = on_state if is_checked else off_state
        field_obj['/V'] = selected_state
        field_obj['/AS'] = selected_state

    for field_name, field_value in field_values.items():
        if field_name in field_name_to_obj:
            field_obj = field_name_to_obj[field_name]
            field_obj['/V'] = pikepdf.String(str(field_value))
            try:
                field_obj['/AS'] = pikepdf.Name(str(field_value))
            except Exception as e:
                logger.debug(f"Unable to set /AS for field '{field_name}': {e}")
            updated_count += 1
            logger.info(f"✓ Updated field '{field_name}' = '{field_value}'")
        else:
            logger.warning(f"✗ Field '{field_name}' not found in PDF")

    for field_name, is_checked in checkbox_field_values.items():
        if field_name in field_name_to_obj:
            field_obj = field_name_to_obj[field_name]
            _set_checkbox(field_obj, is_checked)
            updated_count += 1
            logger.info(f"✓ Updated checkbox '{field_name}' = {is_checked}")
        else:
            logger.warning(f"✗ Checkbox field '{field_name}' not found in PDF")
    
    # Also check page annotations (widget annotations)
    for page_num, page in enumerate(pdf.pages):
        if '/Annots' in page:
            annots = page['/Annots']
            for annot in annots:
                try:
                    if '/Subtype' in annot and annot['/Subtype'] == pikepdf.Name('/Widget'):
                        if '/T' in annot:
                            name = str(annot['/T'])
                            # strip leading slash if present
                            if name.startswith("/"):
                                name = name[1:]
                            if name in field_values:
                                annot['/V'] = pikepdf.String(str(field_values[name]))
                                updated_count += 1
                                logger.info(f"✓ Updated annotation field '{name}' on page {page_num}")
                            elif name in checkbox_field_values:
                                _set_checkbox(annot, checkbox_field_values[name])
                                updated_count += 1
                                logger.info(f"✓ Updated checkbox annotation '{name}' on page {page_num}")
                except Exception as e:
                    logger.debug(f"Error checking annotation: {str(e)}")

    total_targets = len(field_values) + len(checkbox_field_values)
    logger.info(f"Filled {updated_count} out of {total_targets} targeted fields in PDF")
    
    # Write to bytes
    output = BytesIO()
    pdf.save(output)
    output.seek(0)
    return output.getvalue()


def save_filled_pdf_to_s3(user_id: str, submission_id: str, pdf_bytes: bytes) -> Tuple[str, str]:
    """Save filled PDF to S3 and return (key, presigned_download_url)."""
    key = f"submissions/{user_id}/{submission_id}/acord125-filled.pdf"
    if s3_service.s3_client is None:
        # In dev without credentials, just return a pseudo path
        return key, f"/dev/null/{key}"

    # Upload directly using put_object
    s3_service.s3_client.put_object(
        Bucket=s3_service.bucket_name,
        Key=key,
        Body=pdf_bytes,
        ContentType="application/pdf",
    )
    url = s3_service.generate_presigned_download_url(key)
    return key, url


def template_exists() -> bool:
    """Check if the ACORD 125 template file exists on disk."""
    return os.path.isfile(settings.ACORD125_TEMPLATE_PATH)


def list_template_fields() -> List[str]:
    """Attempt to list form field names from the template for mapping verification."""
    template_path = settings.ACORD125_TEMPLATE_PATH
    if not os.path.isfile(template_path):
        return []
    try:
        reader = PdfReader(template_path)
        fields = reader.get_fields()
        if not fields:
            return []
        return list(fields.keys())
    except Exception:
        return []


