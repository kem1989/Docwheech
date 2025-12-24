"""
ACORD form API endpoints

Supports multiple ACORD forms:
- ACORD 125: Commercial Insurance Application
- ACORD 126: Commercial General Liability Section
- ACORD 130: Workers Compensation Application
- ACORD 140: Property Section
"""

from fastapi import APIRouter, HTTPException, Request, Body, Depends
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any, Optional, List

from app.database import get_db
from app.models import Submission
from app.core.acord_schema import ACORD125Schema, create_acord_schema_from_extraction
from app.core.acord_126_schema import ACORD126Schema, create_acord126_from_extraction
from app.core.acord_127_schema import ACORD127Schema, create_acord127_from_extraction
from app.core.acord_130_schema import ACORD130Schema, create_acord130_from_extraction
from app.core.acord_140_schema import ACORD140Schema, create_acord140_from_extraction
from app.core.general_questions import (
    GENERAL_QUESTION_DEFINITIONS,
    get_default_general_question_responses
)
from app.services.pdf_service import (
    generate_filled_pdf_bytes,
    save_filled_pdf_to_s3,
    template_exists,
    list_template_fields,
)
from app.services.multi_form_pdf_service import (
    multi_form_pdf_service,
    ACORDFormType,
    FORM_DISPLAY_NAMES,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/convert")
async def convert_to_acord():
    """Convert extracted data to ACORD schema"""
    # TODO: Implement ACORD conversion logic
    return {"message": "ACORD conversion endpoint - to be implemented"}


@router.get("/schema")
async def get_acord_schema():
    """Get ACORD 125 schema definition"""
    # TODO: Implement schema retrieval
    return {"message": "ACORD schema endpoint - to be implemented"}


@router.post("/fill")
async def fill_acord_form(
    request_body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Fill ACORD 125 PDF and return S3 download URL."""
    try:
        # Extract request parameters
        user_id = request_body.get("user_id")
        submission_id = request_body.get("submission_id")
        acord_data = request_body.get("acord")
        
        if not user_id or not submission_id or not acord_data:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required fields: user_id={user_id}, submission_id={submission_id}, acord={acord_data is not None}"
            )
        
        # Fetch submission to get general_questions
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        general_questions = None
        if submission and submission.general_questions:
            general_questions = submission.general_questions
            logger.info(f"Found {len(general_questions)} general questions for submission {submission_id}")
        else:
            logger.info(f"No general questions found for submission {submission_id}")
        
        # Try to parse ACORD data into schema (lenient validation)
        try:
            # If acord_data is already a dict, use it directly; if it's a string, parse it
            if isinstance(acord_data, str):
                import json
                acord_data = json.loads(acord_data)
            
            acord_schema = ACORD125Schema(**acord_data)
        except ValidationError as ve:
            logger.error(f"ACORD schema validation error: {ve.errors()}")
            logger.error(f"ACORD data received: {type(acord_data)} - {str(acord_data)[:500]}")
            # Still try to create schema with partial data (Pydantic v2)
            try:
                acord_schema = ACORD125Schema.model_validate(acord_data)
            except Exception as e2:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid ACORD schema: {str(e2)}. Validation errors: {ve.errors()}"
                )
        except Exception as e:
            logger.error(f"Error parsing ACORD data: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse ACORD data: {str(e)}"
            )
        
        # Generate filled PDF with general questions
        pdf_bytes = generate_filled_pdf_bytes(acord_schema, general_questions=general_questions)
        key, url = save_filled_pdf_to_s3(user_id, submission_id, pdf_bytes)
        return {"s3_key": key, "download_url": url}
        
    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ACORD 125 template not found. Configure ACORD125_TEMPLATE_PATH.")
    except Exception as e:
        import traceback
        error_detail = f"Failed to generate ACORD 125 PDF: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        raise HTTPException(status_code=500, detail=f"Failed to generate ACORD 125 PDF: {str(e)}")


@router.get("/template-status")
async def get_template_status():
    """Return whether the template exists and any discovered form field names."""
    exists = template_exists()
    fields = list_template_fields() if exists else []
    return {
        "exists": exists,
        "path": "ACORD125_TEMPLATE_PATH",
        "resolved_path": str(__import__('os').path.abspath(__import__('app.config').config.settings.ACORD125_TEMPLATE_PATH)),
        "field_count": len(fields),
        "fields": fields,
    }


@router.get("/general-questions")
async def get_general_questions():
    """Get ACORD 125 General Questions definitions"""
    return {
        "questions": GENERAL_QUESTION_DEFINITIONS,
        "default_responses": get_default_general_question_responses()
    }


# =============================================================================
# MULTI-FORM SUPPORT ENDPOINTS
# =============================================================================

class FillFormRequest(BaseModel):
    """Request for filling a specific form"""
    user_id: str
    submission_id: str
    form_type: str
    data: Dict[str, Any]


class FillMultipleFormsRequest(BaseModel):
    """Request for filling multiple forms"""
    user_id: str
    submission_id: str
    form_types: List[str]
    data: Dict[str, Any]


@router.get("/forms/available")
async def get_available_forms():
    """
    Get list of available ACORD forms that can be generated.
    
    Returns form types with their display names and template availability.
    """
    try:
        forms = multi_form_pdf_service.list_available_forms()
        return {
            "forms": forms,
            "total": len(forms),
            "available_count": sum(1 for f in forms if f.get("template_exists", False))
        }
    except Exception as e:
        logger.error(f"Failed to get available forms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forms/{form_type}/fields")
async def get_form_fields(form_type: str):
    """
    Get all field names from a specific ACORD form template.
    
    Useful for debugging field mappings.
    """
    try:
        form_enum = ACORDFormType(form_type.upper())
        fields = multi_form_pdf_service.get_pdf_field_names(form_enum)
        return {
            "form_type": form_type,
            "display_name": FORM_DISPLAY_NAMES.get(form_enum, form_type),
            "field_count": len(fields),
            "fields": fields
        }
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid form type: {form_type}. Valid types: {[f.value for f in ACORDFormType]}"
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get form fields: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forms/fill")
async def fill_form(
    request: FillFormRequest,
    db: Session = Depends(get_db)
):
    """
    Fill a specific ACORD form with provided data.
    
    Supported form types:
    - ACORD_125: Commercial Insurance Application
    - ACORD_126: Commercial General Liability Section
    - ACORD_130: Workers Compensation Application
    - ACORD_140: Property Section
    """
    try:
        # Validate form type
        try:
            form_enum = ACORDFormType(request.form_type.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid form type: {request.form_type}. Valid types: {[f.value for f in ACORDFormType]}"
            )
        
        # For ACORD 125, use existing logic with general questions
        if form_enum == ACORDFormType.ACORD_125:
            # Fetch general questions from submission
            submission = db.query(Submission).filter(
                Submission.id == request.submission_id
            ).first()
            general_questions = None
            if submission and submission.general_questions:
                general_questions = submission.general_questions
            
            # Create schema
            acord_schema = ACORD125Schema(**request.data)
            
            # Generate PDF
            pdf_bytes = generate_filled_pdf_bytes(acord_schema, general_questions=general_questions)
            key, url = save_filled_pdf_to_s3(request.user_id, request.submission_id, pdf_bytes)
            
            return {
                "form_type": form_enum.value,
                "display_name": FORM_DISPLAY_NAMES.get(form_enum),
                "s3_key": key,
                "download_url": url
            }
        
        # For other forms, use multi-form service
        pdf_bytes = multi_form_pdf_service.fill_form(form_enum, request.data)
        key, url = multi_form_pdf_service.save_to_s3(
            request.user_id,
            request.submission_id,
            form_enum,
            pdf_bytes
        )
        
        return {
            "form_type": form_enum.value,
            "display_name": FORM_DISPLAY_NAMES.get(form_enum),
            "s3_key": key,
            "download_url": url
        }
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fill form: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate form: {str(e)}")


@router.post("/forms/fill-multiple")
async def fill_multiple_forms(
    request: FillMultipleFormsRequest,
    db: Session = Depends(get_db)
):
    """
    Fill multiple ACORD forms at once with the same data.
    
    Returns download URLs for each successfully generated form.
    """
    try:
        results = []
        errors = []
        
        for form_type_str in request.form_types:
            try:
                form_enum = ACORDFormType(form_type_str.upper())
                
                # Handle ACORD 125 specially
                if form_enum == ACORDFormType.ACORD_125:
                    submission = db.query(Submission).filter(
                        Submission.id == request.submission_id
                    ).first()
                    general_questions = None
                    if submission and submission.general_questions:
                        general_questions = submission.general_questions
                    
                    acord_schema = ACORD125Schema(**request.data)
                    pdf_bytes = generate_filled_pdf_bytes(acord_schema, general_questions=general_questions)
                    key, url = save_filled_pdf_to_s3(request.user_id, request.submission_id, pdf_bytes)
                else:
                    pdf_bytes = multi_form_pdf_service.fill_form(form_enum, request.data)
                    key, url = multi_form_pdf_service.save_to_s3(
                        request.user_id,
                        request.submission_id,
                        form_enum,
                        pdf_bytes
                    )
                
                results.append({
                    "form_type": form_enum.value,
                    "display_name": FORM_DISPLAY_NAMES.get(form_enum),
                    "s3_key": key,
                    "download_url": url,
                    "success": True
                })
                
            except Exception as e:
                errors.append({
                    "form_type": form_type_str,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "submission_id": request.submission_id,
            "total_requested": len(request.form_types),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Failed to fill multiple forms: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate forms: {str(e)}")


@router.post("/forms/generate-from-extraction")
async def generate_forms_from_extraction(
    request_body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Generate multiple ACORD forms from extraction data.
    
    This endpoint takes raw extracted data and automatically populates
    the appropriate schemas for each form type requested.
    
    Request body:
    - user_id: User ID
    - submission_id: Submission ID
    - form_types: List of form types to generate (e.g., ["ACORD_125", "ACORD_126"])
    - extracted_data: Raw extracted data from AI extraction
    - acord_schema: Optional pre-processed ACORD schema
    """
    try:
        user_id = request_body.get("user_id")
        submission_id = request_body.get("submission_id")
        form_types = request_body.get("form_types", ["ACORD_125"])
        extracted_data = request_body.get("extracted_data", {})
        acord_schema = request_body.get("acord_schema", {})
        
        if not user_id or not submission_id:
            raise HTTPException(status_code=422, detail="Missing user_id or submission_id")
        
        results = []
        
        for form_type_str in form_types:
            try:
                form_enum = ACORDFormType(form_type_str.upper())
                
                # Generate form-specific data
                if form_enum == ACORDFormType.ACORD_125:
                    if acord_schema:
                        schema = ACORD125Schema(**acord_schema)
                    else:
                        schema = create_acord_schema_from_extraction(extracted_data)
                    
                    # Get general questions
                    submission = db.query(Submission).filter(
                        Submission.id == submission_id
                    ).first()
                    general_questions = submission.general_questions if submission else None
                    
                    pdf_bytes = generate_filled_pdf_bytes(schema, general_questions=general_questions)
                    key, url = save_filled_pdf_to_s3(user_id, submission_id, pdf_bytes)
                    
                elif form_enum == ACORDFormType.ACORD_126:
                    schema = create_acord126_from_extraction(extracted_data)
                    pdf_bytes = multi_form_pdf_service.fill_form(form_enum, schema.to_dict())
                    key, url = multi_form_pdf_service.save_to_s3(user_id, submission_id, form_enum, pdf_bytes)
                    
                elif form_enum == ACORDFormType.ACORD_130:
                    schema = create_acord130_from_extraction(extracted_data)
                    pdf_bytes = multi_form_pdf_service.fill_form(form_enum, schema.to_dict())
                    key, url = multi_form_pdf_service.save_to_s3(user_id, submission_id, form_enum, pdf_bytes)
                    
                elif form_enum == ACORDFormType.ACORD_140:
                    schema = create_acord140_from_extraction(extracted_data)
                    pdf_bytes = multi_form_pdf_service.fill_form(form_enum, schema.to_dict())
                    key, url = multi_form_pdf_service.save_to_s3(user_id, submission_id, form_enum, pdf_bytes)
                
                elif form_enum == ACORDFormType.ACORD_127:
                    schema = create_acord127_from_extraction(extracted_data)
                    pdf_bytes = multi_form_pdf_service.fill_form(form_enum, schema.to_dict())
                    key, url = multi_form_pdf_service.save_to_s3(user_id, submission_id, form_enum, pdf_bytes)
                
                else:
                    # Unknown form type - skip
                    raise ValueError(f"Unsupported form type: {form_enum.value}")
                
                results.append({
                    "form_type": form_enum.value,
                    "display_name": FORM_DISPLAY_NAMES.get(form_enum),
                    "s3_key": key,
                    "download_url": url,
                    "success": True
                })
                
            except Exception as e:
                logger.error(f"Failed to generate {form_type_str}: {e}")
                results.append({
                    "form_type": form_type_str,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "submission_id": submission_id,
            "results": results,
            "successful": sum(1 for r in results if r.get("success")),
            "total": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate forms from extraction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
