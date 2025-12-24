"""
Gap Detection API endpoints

Provides context-aware analysis of submission completeness
based on the specific coverages being requested.
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.gap_detection_service import gap_detection_service
from app.services.extraction_db_service import ExtractionDatabaseService
from app.core.security import get_current_user
from app.core.coverage_requirements import get_all_coverage_types, get_requirements_for_coverages
from app.models.user import User
from app.models.submission import Submission
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================

class GapAnalysisRequest(BaseModel):
    """Request model for gap analysis"""
    submission_id: str = Field(..., description="Submission ID to analyze")
    use_ai_enhancement: bool = Field(True, description="Whether to use AI for additional insights")


class MissingDataItem(BaseModel):
    """A missing data field"""
    id: str
    label: str
    field_path: str
    section: Optional[str] = None
    acord_field: Optional[str] = None
    severity: str
    for_coverage: str
    reason: str
    current_value: Optional[str] = None


class MissingSectionItem(BaseModel):
    """Missing data grouped by section"""
    section: str
    section_display: str
    missing_count: int
    has_critical: bool
    fields: List[MissingDataItem]


class ConditionalGapItem(BaseModel):
    """A conditional requirement that was triggered"""
    id: str
    label: str
    severity: str
    for_coverage: str
    triggered_by: str
    status: str


class AIInsight(BaseModel):
    """An AI-generated insight"""
    type: str
    message: str
    priority: str


class CoverageInfo(BaseModel):
    """Coverage type information"""
    code: str
    display_name: str


class GapAnalysisResponse(BaseModel):
    """Response model for gap analysis"""
    analysis_timestamp: str
    detected_coverages: List[CoverageInfo]
    completeness_score: int
    ready_to_submit: bool
    summary: str
    missing_data: List[MissingDataItem]  # Flat list for backward compatibility
    missing_data_by_section: List[MissingSectionItem]  # Grouped by section for display
    conditional_gaps: List[ConditionalGapItem]
    ai_insights: List[dict]
    total_requirements: int
    found_items: int
    total_missing: int
    critical_missing: int


class CoverageType(BaseModel):
    """Coverage type with display name"""
    code: str
    display_name: str
    short_name: str


class CoverageRequirementsResponse(BaseModel):
    """Response with requirements for specific coverages"""
    coverage_types: List[str]
    required_documents: List[dict]
    required_data: List[dict]
    conditional_requirements: List[dict]


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/analyze", response_model=GapAnalysisResponse)
async def analyze_submission_gaps(
    request: GapAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a submission for completeness based on detected coverages.
    
    This endpoint:
    1. Detects which insurance coverages are being requested
    2. Checks extracted data for required fields specific to those coverages
    3. Optionally uses AI to provide additional insights
    
    Returns a detailed report with missing data fields and a completeness score.
    """
    try:
        logger.info(f"Analyzing gaps for submission {request.submission_id}")
        
        # Get extraction results from database
        db_service = ExtractionDatabaseService(db)
        results = db_service.get_extraction_results(request.submission_id, str(current_user.id))
        
        if not results:
            raise HTTPException(
                status_code=404, 
                detail="Extraction results not found. Please complete data extraction first."
            )
        
        extracted_data = results.get("extracted_data", {})
        acord_schema = results.get("acord_schema", {})
        
        # Run gap analysis
        report = await gap_detection_service.analyze_submission(
            extracted_data=extracted_data,
            acord_schema=acord_schema,
            use_ai_enhancement=request.use_ai_enhancement
        )
        
        # Save results to database
        submission = db.query(Submission).filter(Submission.id == request.submission_id).first()
        if submission:
            submission.gap_analysis_results = report
            submission.gap_analysis_timestamp = datetime.utcnow()
            db.commit()
            logger.info(f"Saved gap analysis results for submission {request.submission_id}")
        
        logger.info(
            f"Gap analysis complete for {request.submission_id}: "
            f"Score={report['completeness_score']}%, "
            f"Missing data={len(report['missing_data'])}"
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gap analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {str(e)}")


@router.get("/coverage-types", response_model=List[CoverageType])
async def get_coverage_types():
    """
    Get list of all supported coverage types.
    
    Returns the coverage codes and display names that the system recognizes.
    """
    try:
        return get_all_coverage_types()
    except Exception as e:
        logger.error(f"Failed to get coverage types: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/requirements", response_model=CoverageRequirementsResponse)
async def get_coverage_requirements(
    coverage_types: List[str]
):
    """
    Get the requirements for specific coverage types.
    
    Use this to see what documents and data are needed for
    specific insurance coverages before starting a submission.
    """
    try:
        if not coverage_types:
            raise HTTPException(
                status_code=400, 
                detail="At least one coverage type is required"
            )
        
        # Normalize coverage types
        normalized = [ct.upper().replace(" ", "_") for ct in coverage_types]
        
        requirements = get_requirements_for_coverages(normalized)
        return requirements
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get requirements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-analyze")
async def test_analyze_gaps(request: GapAnalysisRequest):
    """
    Test endpoint for gap analysis (no authentication required).
    Returns mock data for testing purposes.
    """
    try:
        logger.info(f"Test gap analysis for submission {request.submission_id}")
        
        # Return mock response
        return {
            "analysis_timestamp": "2024-01-15T10:30:00Z",
            "detected_coverages": [
                {"code": "COMMERCIAL_GENERAL_LIABILITY", "display_name": "Commercial General Liability"},
                {"code": "BUSINESS_AUTO", "display_name": "Commercial Auto"}
            ],
            "completeness_score": 72,
            "ready_to_submit": False,
            "summary": "Good progress on this Commercial General Liability, Commercial Auto submission. A few items need attention before submitting to carriers.",
            "missing_data": [
                {
                    "id": "vehicle_vins",
                    "label": "Vehicle VINs",
                    "field_path": "vehicles",
                    "severity": "critical",
                    "for_coverage": "BUSINESS_AUTO",
                    "reason": "No items found",
                    "current_value": None
                },
                {
                    "id": "driver_info",
                    "label": "Driver Information (Name, DOB, License)",
                    "field_path": "drivers",
                    "severity": "critical",
                    "for_coverage": "BUSINESS_AUTO",
                    "reason": "No items found in list",
                    "current_value": None
                }
            ],
            "conditional_gaps": [],
            "ai_insights": [
                {
                    "type": "recommendation",
                    "message": "Based on the trucking operations described, you should also consider Motor Cargo coverage for goods in transit.",
                    "priority": "medium"
                },
                {
                    "type": "warning",
                    "message": "Vehicle and driver details are missing from extracted data. Ensure the source documents contain this information.",
                    "priority": "high"
                }
            ],
            "total_requirements": 18,
            "found_items": 14
        }
        
    except Exception as e:
        logger.error(f"Test gap analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{submission_id}", response_model=GapAnalysisResponse)
async def get_gap_analysis(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get stored gap analysis results for a submission.
    
    Returns the most recent gap analysis results if available.
    Returns 404 if no analysis has been run yet.
    
    Note: This route must come after all specific routes (like /coverage-types)
    to avoid route conflicts.
    """
    try:
        # Get submission and verify ownership
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=404,
                detail="Submission not found"
            )
        
        if not submission.gap_analysis_results:
            raise HTTPException(
                status_code=404,
                detail="No gap analysis results found. Please run analysis first."
            )
        
        return submission.gap_analysis_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get gap analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get gap analysis: {str(e)}")



