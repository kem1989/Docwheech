"""
ACORD form API endpoints
"""

from fastapi import APIRouter, HTTPException, Request, Body, Depends
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any, Optional

from app.database import get_db
from app.models import Submission
from app.core.acord_schema import ACORD125Schema
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
