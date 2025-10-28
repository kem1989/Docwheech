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
    
    db = SessionLocal()
    db_service = ExtractionDatabaseService(db)
    
    try:
        print(f"=== Running AI extraction task for submission {submission_id} ===")
        logger.info(f"Running AI extraction task for submission {submission_id}")
        
        # Step 1: Document Analysis (0-20%)
        logger.info(f"=== CHECKPOINT 1: About to update to 10% ===")
        db_service.update_extraction_progress(submission_id, 10, "processing")
        print(f"=== Step 1: Document Analysis - 10% ===")
        logger.info(f"=== CHECKPOINT 2: Updated to 10%, now updating to 20% ===")
        
        db_service.update_extraction_progress(submission_id, 20, "processing")
        logger.info(f"=== CHECKPOINT 3: Updated to 20% ===")
        print(f"=== Step 2: Text Extraction Starting - 20% ===")
        logger.info(f"=== CHECKPOINT 4: About to define callback ===")
        
        # Define progress callback to update database during extraction
        def update_progress(progress: int):
            """Callback to update progress in database during extraction"""
            try:
                db_service.update_extraction_progress(submission_id, progress, "processing")
                print(f"=== Progress Update: {progress}% ===")
                logger.info(f"Extraction progress for {submission_id}: {progress}%")
            except Exception as e:
                logger.error(f"Failed to update progress: {str(e)}")
        
        # Run the AI extraction with progress callback
        print(f"=== Starting AI extraction with real-time progress updates ===")
        logger.info("Starting AI extraction with progress callback")
        
        try:
            extraction_result = await ai_extraction_service.extract_from_documents(
                submission_id=submission_id,
                document_keys=document_keys,
                user_id=user_id,
                confidence_threshold=confidence_threshold,
                progress_callback=update_progress
            )
            print(f"=== AI extraction completed ===")
            logger.info("AI extraction service call completed successfully")
        except HTTPException as http_err:
            # HTTPExceptions from services need to be converted to regular exceptions in background tasks
            error_msg = http_err.detail if hasattr(http_err, 'detail') else str(http_err)
            logger.error(f"HTTP error in extraction service: {error_msg}")
            raise Exception(error_msg)
        except Exception as extraction_err:
            logger.error(f"Extraction service error: {str(extraction_err)}", exc_info=True)
            raise
        
        # Final progress update before saving (90-100%)
        db_service.update_extraction_progress(submission_id, 90, "processing")
        print(f"=== Finalizing results - 90% ===")
        
        db_service.update_extraction_progress(submission_id, 95, "processing")
        print(f"=== Saving to database - 95% ===")
        
        # Save extraction results to database
        success = db_service.save_extraction_results(submission_id, extraction_result)
        
        if success:
            logger.info(f"AI extraction completed for submission {submission_id}")
            print(f"=== Extraction results saved successfully - 100% ===")
        else:
            logger.error(f"Failed to save extraction results for submission {submission_id}")
            raise Exception("Failed to save extraction results to database")
        
    except Exception as e:
        error_msg = f"AI extraction task failed for submission {submission_id}: {str(e)}"
        print(f"=== ERROR: {error_msg} ===")
        logger.error(error_msg, exc_info=True)
        db_service.save_extraction_error(submission_id, str(e))
    finally:
        db.close()
