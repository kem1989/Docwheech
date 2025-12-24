"""
AI extraction API endpoints
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.ai_extraction_service import ai_extraction_service
from app.services.extraction_db_service import ExtractionDatabaseService
from app.core.security import get_current_user
from app.models.user import User
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


class ExtractionRequest(BaseModel):
    """Request model for AI extraction"""
    submission_id: str
    document_keys: List[str]
    confidence_threshold: float = 0.7


class ExtractionResponse(BaseModel):
    """Response model for AI extraction"""
    extraction_id: str
    status: str
    message: str
    estimated_completion_time: str = "2-5 minutes"


class ExtractionStatusResponse(BaseModel):
    """Response model for extraction status"""
    submission_id: str
    status: str
    extraction_status: str
    extraction_progress: int
    total_files: int
    processed_files: int
    created_at: str
    updated_at: str
    completed_at: str | None = None
    extraction_error: str | None = None


class FieldUpdateRequest(BaseModel):
    """Request model for updating a single field"""
    field_path: str
    new_value: Any


class MultiFieldUpdateRequest(BaseModel):
    """Request model for updating multiple fields"""
    changes: Dict[str, Any]  # field_path -> new_value


class FieldUpdateResponse(BaseModel):
    """Response model for field update"""
    success: bool
    field_path: str
    old_value: Any
    new_value: Any
    updated_at: str


class MultiFieldUpdateResponse(BaseModel):
    """Response model for multiple field updates"""
    success: bool
    updated_fields: List[str]
    failed_fields: List[str]
    updated_at: str


class EditHistoryEntry(BaseModel):
    """Model for a single edit history entry"""
    field_path: str
    old_value: Any
    new_value: Any
    edited_at: str
    edited_by: str | None = None


class EditHistoryResponse(BaseModel):
    """Response model for edit history"""
    submission_id: str
    edit_history: List[EditHistoryEntry]


@router.post("/extract", response_model=ExtractionResponse)
async def extract_data(
    request: ExtractionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract data from uploaded files using AI
    
    This endpoint triggers the AI extraction process using OpenAI GPT-4 and AWS Textract.
    The extraction runs in the background and results can be retrieved using the extraction_id.
    """
    try:
        logger.info(f"Starting AI extraction for user {current_user.id}, submission {request.submission_id}")
        
        # Validate document keys
        if not request.document_keys:
            raise HTTPException(status_code=400, detail="No documents provided for extraction")
        
        # Validate confidence threshold
        if not 0.0 <= request.confidence_threshold <= 1.0:
            raise HTTPException(status_code=400, detail="Confidence threshold must be between 0.0 and 1.0")
        
        # Create extraction job in database
        db_service = ExtractionDatabaseService(db)
        db_service.create_extraction_job(
            submission_id=request.submission_id,
            user_id=str(current_user.id),
            document_keys=request.document_keys,
            confidence_threshold=request.confidence_threshold
        )
        
        # Start extraction in background
        background_tasks.add_task(
            _run_extraction_task,
            request.submission_id,
            request.document_keys,
            str(current_user.id),
            request.confidence_threshold
        )
        
        return ExtractionResponse(
            extraction_id=request.submission_id,
            status="processing",
            message="AI extraction started successfully",
            estimated_completion_time="2-5 minutes"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start AI extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start extraction: {str(e)}")


@router.post("/test-extract")
async def test_extract_data(request: ExtractionRequest):
    """
    Test endpoint for AI extraction (no authentication required)
    This endpoint is for testing purposes only
    """
    try:
        logger.info(f"Test extraction started for submission {request.submission_id}")
        
        # Validate document keys
        if not request.document_keys:
            raise HTTPException(status_code=400, detail="No documents provided for extraction")
        
        # Validate confidence threshold
        if not 0.0 <= request.confidence_threshold <= 1.0:
            raise HTTPException(status_code=400, detail="Confidence threshold must be between 0.0 and 1.0")
        
        # Return mock response for testing
        return ExtractionResponse(
            extraction_id=request.submission_id,
            status="processing",
            message="Test extraction started successfully (mock response)",
            estimated_completion_time="2-5 minutes"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start test extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start test extraction: {str(e)}")


@router.get("/test-extraction/{extraction_id}/status")
async def test_get_extraction_status(extraction_id: str):
    """Test endpoint to get extraction status (no authentication required)"""
    try:
        logger.info(f"Checking test extraction status for {extraction_id}")
        
        # Return mock status for testing
        return {
            "submission_id": extraction_id,
            "status": "completed",
            "extraction_status": "completed",
            "extraction_progress": 100,
            "total_files": 1,
            "processed_files": 1,
            "created_at": "2024-01-15T10:25:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to get test extraction status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get test status: {str(e)}")


@router.get("/test-extraction/{extraction_id}")
async def test_get_extraction_result(extraction_id: str):
    """
    Test endpoint to get extraction results (no authentication required)
    Returns mock data for testing purposes
    """
    try:
        logger.info(f"Retrieving test extraction results for {extraction_id}")
        
        # Return mock results for testing
        return {
            "extraction_id": extraction_id,
            "status": "completed",
            "extracted_data": {
                "insured_information": {
                    "company_name": {
                        "value": "Test Company Inc.",
                        "confidence": 0.95,
                        "validation_status": "validated"
                    },
                    "business_address": {
                        "value": "123 Test Street, Dallas, TX 75201",
                        "confidence": 0.88,
                        "validation_status": "validated"
                    },
                    "phone": {
                        "value": "(214) 555-1234",
                        "confidence": 0.92,
                        "validation_status": "validated"
                    }
                },
                "policy_information": {
                    "coverage_type": {
                        "value": "General Liability",
                        "confidence": 0.92,
                        "validation_status": "validated"
                    },
                    "effective_date": {
                        "value": "2024-01-01",
                        "confidence": 0.85,
                        "validation_status": "validated"
                    },
                    "premium_amount": {
                        "value": 15000,
                        "confidence": 0.90,
                        "validation_status": "validated"
                    }
                },
                "broker_information": {
                    "broker_name": {
                        "value": "John Test Broker",
                        "confidence": 0.88,
                        "validation_status": "validated"
                    },
                    "broker_email": {
                        "value": "john@testagency.com",
                        "confidence": 0.95,
                        "validation_status": "validated"
                    }
                }
            },
            "acord_schema": {
                "insured_information": {
                    "company_name": "Test Company Inc.",
                    "business_address": "123 Test Street, Dallas, TX 75201",
                    "city": "Dallas",
                    "state": "TX",
                    "zip_code": "75201",
                    "phone": "(214) 555-1234"
                },
                "policy_information": {
                    "coverage_type": "General Liability",
                    "effective_date": "2024-01-01",
                    "premium_amount": 15000
                },
                "broker_information": {
                    "broker_name": "John Test Broker",
                    "broker_email": "john@testagency.com"
                }
            },
            "risk_narrative": "This is a test risk narrative generated for testing purposes. The company appears to be a well-established business with standard operations and minimal risk factors.",
            "processing_stats": {
                "total_documents": 1,
                "total_pages": 2,
                "average_confidence": 0.89,
                "extraction_method": "openai_gpt4_textract",
                "completion_percentage": 85.5,
                "missing_fields": ["insured_information.federal_tax_id", "policy_information.policy_number"]
            },
            "extraction_timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve test extraction results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve test results: {str(e)}")


@router.get("/{extraction_id}/status", response_model=ExtractionStatusResponse)
async def get_extraction_status(
    extraction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current status of an extraction job"""
    try:
        logger.info(f"Checking extraction status for {extraction_id}")
        
        # Get extraction status from database
        db_service = ExtractionDatabaseService(db)
        status_data = db_service.get_extraction_status(extraction_id, str(current_user.id))
        
        if not status_data:
            raise HTTPException(status_code=404, detail="Extraction not found")
        
        logger.info(f"Returning status: {status_data['extraction_status']} - {status_data['extraction_progress']}%")
        
        # Ensure all required fields are present
        response = ExtractionStatusResponse(
            submission_id=status_data['submission_id'],
            status=status_data['status'],
            extraction_status=status_data['extraction_status'],
            extraction_progress=status_data['extraction_progress'],
            total_files=status_data['total_files'],
            processed_files=status_data['processed_files'],
            created_at=status_data['created_at'] or '',
            updated_at=status_data['updated_at'] or '',
            completed_at=status_data.get('completed_at'),
            extraction_error=status_data.get('extraction_error')
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get extraction status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/extraction/{extraction_id}")
async def get_extraction_result(
    extraction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get extraction results by extraction ID
    
    Returns the structured data extracted from documents, including:
    - Insured information (company name, address, contact details)
    - Policy information (coverage type, dates, premium)
    - Broker information (agent details)
    - Risk information (business details, revenue, employees)
    - Generated risk narrative
    """
    try:
        logger.info(f"Retrieving extraction results for {extraction_id}")
        
        # Get extraction results from database
        db_service = ExtractionDatabaseService(db)
        results = db_service.get_extraction_results(extraction_id, str(current_user.id))
        
        if not results:
            raise HTTPException(status_code=404, detail="Extraction not found or not completed")
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to retrieve extraction results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")


# =============================================================================
# FIELD EDITING ENDPOINTS
# =============================================================================

@router.patch("/{submission_id}/field", response_model=FieldUpdateResponse)
async def update_extracted_field(
    submission_id: str,
    request: FieldUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a single extracted field value.
    
    This endpoint allows brokers to manually correct or update extracted data.
    Changes are tracked for audit purposes and the field confidence is set to 1.0
    to indicate it was manually verified.
    """
    try:
        logger.info(f"Updating field {request.field_path} for submission {submission_id}")
        
        db_service = ExtractionDatabaseService(db)
        
        # Get current value before update
        old_value = db_service.get_field_value(submission_id, request.field_path)
        
        # Update the field
        success = db_service.update_extracted_field(
            submission_id=submission_id,
            field_path=request.field_path,
            new_value=request.new_value,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Submission or field not found")
        
        from datetime import datetime
        return FieldUpdateResponse(
            success=True,
            field_path=request.field_path,
            old_value=old_value,
            new_value=request.new_value,
            updated_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update field: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update field: {str(e)}")


@router.patch("/{submission_id}/fields", response_model=MultiFieldUpdateResponse)
async def update_multiple_extracted_fields(
    submission_id: str,
    request: MultiFieldUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update multiple extracted fields at once.
    
    Useful for batch updates when multiple fields are edited before saving.
    """
    try:
        logger.info(f"Updating {len(request.changes)} fields for submission {submission_id}")
        
        db_service = ExtractionDatabaseService(db)
        
        updated_fields = []
        failed_fields = []
        
        for field_path, new_value in request.changes.items():
            try:
                success = db_service.update_extracted_field(
                    submission_id=submission_id,
                    field_path=field_path,
                    new_value=new_value,
                    user_id=str(current_user.id)
                )
                
                if success:
                    updated_fields.append(field_path)
                else:
                    failed_fields.append(field_path)
                    
            except Exception as e:
                logger.warning(f"Failed to update field {field_path}: {str(e)}")
                failed_fields.append(field_path)
        
        from datetime import datetime
        return MultiFieldUpdateResponse(
            success=len(failed_fields) == 0,
            updated_fields=updated_fields,
            failed_fields=failed_fields,
            updated_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to update fields: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update fields: {str(e)}")


@router.get("/{submission_id}/edit-history", response_model=EditHistoryResponse)
async def get_field_edit_history(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the edit history for a submission.
    
    Returns all field edits made to the extracted data, useful for
    auditing and reviewing changes.
    """
    try:
        logger.info(f"Getting edit history for submission {submission_id}")
        
        db_service = ExtractionDatabaseService(db)
        history = db_service.get_edit_history(submission_id)
        
        return EditHistoryResponse(
            submission_id=submission_id,
            edit_history=[
                EditHistoryEntry(
                    field_path=entry['field_path'],
                    old_value=entry['old_value'],
                    new_value=entry['new_value'],
                    edited_at=entry['edited_at'],
                    edited_by=entry.get('edited_by')
                )
                for entry in history
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to get edit history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get edit history: {str(e)}")


async def _run_extraction_task(
    submission_id: str,
    document_keys: List[str],
    user_id: str,
    confidence_threshold: float
):
    """
    Background task to run AI extraction
    
    This function runs the actual AI extraction process and stores results in the database.
    Progress updates align with frontend processing steps:
    - 0-20%: Document Analysis
    - 20-40%: Text Extraction (AWS Textract)
    - 40-60%: AI Processing (OpenAI GPT-4)
    - 60-80%: Data Validation
    - 80-100%: ACORD Mapping
    """
    from app.database import SessionLocal
    import traceback
    
    db = SessionLocal()
    db_service = ExtractionDatabaseService(db)
    
    try:
        logger.info(f"")
        logger.info(f"{'='*60}")
        logger.info(f"STARTING AI EXTRACTION TASK")
        logger.info(f"Submission ID: {submission_id}")
        logger.info(f"Documents: {len(document_keys)}")
        for i, key in enumerate(document_keys):
            logger.info(f"  Doc {i+1}: {key}")
        logger.info(f"{'='*60}")
        
        # Step 1: Document Analysis (0-20%)
        logger.info(f"Step 1: Document Analysis - updating to 10%")
        db_service.update_extraction_progress(submission_id, 10, "processing")
        
        db_service.update_extraction_progress(submission_id, 20, "processing")
        logger.info(f"Step 2: Starting Text Extraction (Textract) - 20%")
        
        # Define progress callback to update database during extraction
        def update_progress(progress: int):
            """Callback to update progress in database during extraction"""
            try:
                db_service.update_extraction_progress(submission_id, progress, "processing")
                logger.info(f"Progress update: {progress}%")
            except Exception as e:
                logger.error(f"Failed to update progress: {str(e)}")
        
        # Run the AI extraction with progress callback
        logger.info("Calling AI extraction service...")
        
        try:
            extraction_result = await ai_extraction_service.extract_from_documents(
                submission_id=submission_id,
                document_keys=document_keys,
                user_id=user_id,
                confidence_threshold=confidence_threshold,
                progress_callback=update_progress
            )
            logger.info("AI extraction service completed successfully")
        except HTTPException as http_err:
            # HTTPExceptions from services need to be converted to regular exceptions in background tasks
            error_detail = http_err.detail if hasattr(http_err, 'detail') else str(http_err)
            logger.error(f"HTTP error in extraction service: {error_detail}")
            logger.error(f"HTTP status code: {http_err.status_code}")
            raise Exception(f"Extraction error (HTTP {http_err.status_code}): {error_detail}")
        except Exception as extraction_err:
            # Get the full traceback for debugging
            tb_str = traceback.format_exc()
            logger.error(f"Extraction service error: {str(extraction_err)}")
            logger.error(f"Full traceback:\n{tb_str}")
            raise Exception(f"Extraction failed: {str(extraction_err)}")
        
        # Final progress update before saving (90-100%)
        db_service.update_extraction_progress(submission_id, 90, "processing")
        logger.info("Step 6: Finalizing results - 90%")
        
        db_service.update_extraction_progress(submission_id, 95, "processing")
        logger.info("Step 7: Saving to database - 95%")
        
        # Save extraction results to database
        success = db_service.save_extraction_results(submission_id, extraction_result)
        
        if success:
            logger.info(f"{'='*60}")
            logger.info(f"AI EXTRACTION COMPLETED SUCCESSFULLY")
            logger.info(f"Submission ID: {submission_id}")
            logger.info(f"{'='*60}")
        else:
            logger.error(f"Failed to save extraction results for submission {submission_id}")
            raise Exception("Failed to save extraction results to database")
        
    except Exception as e:
        # Capture detailed error information
        error_details = str(e)
        if not error_details or error_details == "":
            error_details = f"Unknown error: {type(e).__name__}"
        
        # Get traceback for logging
        tb_str = traceback.format_exc()
        
        logger.error(f"{'='*60}")
        logger.error(f"AI EXTRACTION FAILED")
        logger.error(f"Submission ID: {submission_id}")
        logger.error(f"Error: {error_details}")
        logger.error(f"Traceback:\n{tb_str}")
        logger.error(f"{'='*60}")
        
        # Save the detailed error to database
        db_service.save_extraction_error(submission_id, error_details)
    finally:
        db.close()
