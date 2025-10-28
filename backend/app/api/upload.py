"""
File upload API endpoints
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
import uuid
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_active_user
from app.models import User, Submission, Document
from app.schemas.submission import (
    SubmissionCreate, SubmissionResponse, SubmissionSummary,
    FileUploadRequest, FileUploadResponse, DocumentResponse,
    DocumentListResponse, FileInfo
)
from app.services.s3_service import s3_service
from app.services.file_validation import file_validation_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/submissions", response_model=SubmissionResponse)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new submission"""
    try:
        # Create new submission
        submission = Submission(
            user_id=current_user.id,
            title=submission_data.title,
            submission_type=submission_data.submission_type.value,
            status="draft"
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        logger.info(f"Created submission {submission.id} for user {current_user.id}")
        return submission
        
    except Exception as e:
        logger.error(f"Failed to create submission: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create submission"
        )


@router.get("/submissions", response_model=List[SubmissionSummary])
async def get_user_submissions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all submissions for the current user"""
    try:
        submissions = db.query(Submission).filter(
            Submission.user_id == current_user.id
        ).order_by(Submission.created_at.desc()).all()
        
        return submissions
        
    except Exception as e:
        logger.error(f"Failed to get submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get submissions"
        )


@router.get("/submissions/incomplete", response_model=List[SubmissionSummary])
async def get_incomplete_submissions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get incomplete submissions for session recovery"""
    try:
        # Get submissions that are draft or processing status
        incomplete_submissions = db.query(Submission).filter(
            Submission.user_id == current_user.id,
            Submission.status.in_(["draft", "processing"])
        ).order_by(Submission.updated_at.desc()).all()
        
        return incomplete_submissions
        
    except Exception as e:
        logger.error(f"Failed to get incomplete submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get incomplete submissions"
        )


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific submission"""
    try:
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        return submission
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get submission"
        )


@router.post("/submissions/{submission_id}/upload-urls", response_model=FileUploadResponse)
async def generate_upload_urls(
    submission_id: str,
    file_names: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate presigned upload URLs for files"""
    try:
        # Verify submission exists and belongs to user
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Generate upload URLs for each file
        upload_urls = {}
        
        for filename in file_names:
            # Validate filename
            if not filename or '.' not in filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid filename: {filename}"
                )
            
            # Generate S3 key
            s3_key = s3_service.generate_upload_key(
                str(current_user.id),
                str(submission_id),
                filename
            )
            
            # Get file extension for content type
            file_extension = filename.split('.')[-1].lower()
            content_type_map = {
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png'
            }
            content_type = content_type_map.get(file_extension, 'application/octet-stream')
            
            # Generate presigned upload URL
            upload_data = s3_service.generate_presigned_upload_url(
                s3_key, content_type, expires_in=3600
            )
            
            upload_urls[filename] = {
                'upload_url': upload_data['url'],
                'fields': upload_data['fields'],
                's3_key': s3_key,
                'content_type': content_type
            }
        
        return FileUploadResponse(
            submission_id=submission_id,
            upload_urls=upload_urls,
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate upload URLs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URLs"
        )


@router.post("/submissions/{submission_id}/files")
async def confirm_file_upload(
    submission_id: str,
    file_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Confirm file upload and create document record"""
    try:
        # Verify submission exists and belongs to user
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Extract file information
        filename = file_data.get('filename')
        s3_key = file_data.get('s3_key')
        file_size = file_data.get('file_size', 0)
        content_type = file_data.get('content_type', 'application/octet-stream')
        
        if not all([filename, s3_key]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required file information"
            )
        
        # Get file extension and type
        file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        # Create document record
        document = Document(
            submission_id=submission_id,
            original_filename=filename,
            file_type=file_extension,
            file_size=file_size,
            mime_type=content_type,
            s3_bucket=s3_service.bucket_name,
            s3_key=s3_key,
            processing_status="uploaded"
        )
        
        db.add(document)
        
        # Update submission file count
        submission.total_files += 1
        submission.updated_at = datetime.utcnow()
        
        # Reset extraction status if submission previously failed
        # This allows users to retry extraction with new/updated files
        if submission.extraction_status == 'failed':
            logger.info(f"Resetting extraction status for submission {submission_id} from 'failed' to 'pending'")
            submission.extraction_status = 'pending'
            submission.extraction_error = None
            submission.extraction_progress = 0
            submission.processed_files = 0
            submission.status = 'draft'
        
        db.commit()
        db.refresh(document)
        
        logger.info(f"Created document record {document.id} for file {filename}")
        
        return {
            "message": "File upload confirmed",
            "document_id": str(document.id),
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to confirm file upload: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm file upload"
        )


@router.post("/submissions/{submission_id}/reset-extraction")
async def reset_extraction_status(
    submission_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reset extraction status for a failed submission to allow retry"""
    try:
        # Verify submission exists and belongs to user
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Reset extraction status
        logger.info(f"Manually resetting extraction status for submission {submission_id}")
        submission.extraction_status = 'pending'
        submission.extraction_error = None
        submission.extraction_progress = 0
        submission.processed_files = 0
        submission.status = 'draft'
        submission.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(submission)
        
        return {
            "message": "Extraction status reset successfully",
            "submission_id": str(submission.id),
            "extraction_status": submission.extraction_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset extraction status: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset extraction status"
        )


@router.get("/submissions/{submission_id}/files", response_model=DocumentListResponse)
async def get_submission_files(
    submission_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all files for a submission"""
    try:
        # Verify submission exists and belongs to user
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Get documents
        documents = db.query(Document).filter(
            Document.submission_id == submission_id
        ).order_by(Document.created_at.desc()).all()
        
        # Generate download URLs for documents
        for doc in documents:
            if doc.s3_key:
                try:
                    doc.s3_url = s3_service.generate_presigned_download_url(
                        doc.s3_key, expires_in=3600
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate download URL for {doc.s3_key}: {str(e)}")
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents),
            submission_id=submission_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get submission files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get submission files"
        )


@router.delete("/files/{document_id}")
async def delete_file(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a file from submission"""
    try:
        # Get document and verify ownership
        document = db.query(Document).join(Submission).filter(
            Document.id == document_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete from S3
        if document.s3_key:
            s3_service.delete_file(document.s3_key)
        
        # Update submission file count
        submission = document.submission
        submission.total_files = max(0, submission.total_files - 1)
        submission.updated_at = datetime.utcnow()
        
        # Delete document record
        db.delete(document)
        db.commit()
        
        logger.info(f"Deleted file {document.original_filename} from submission {submission.id}")
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@router.post("/files/validate")
async def validate_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Validate a file before upload"""
    try:
        # Read file content
        content = await file.read()
        
        # Validate file
        file_info = file_validation_service.get_file_info(file.filename, content)
        
        return FileInfo(**file_info)
        
    except Exception as e:
        logger.error(f"File validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File validation failed: {str(e)}"
        )


@router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a submission and all its related data
    
    This will delete:
    - All documents from S3 storage
    - All document records from database
    - All ACORD data records
    - The submission itself
    """
    try:
        # Get submission and verify ownership
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Get all documents for this submission
        documents = db.query(Document).filter(
            Document.submission_id == submission_id
        ).all()
        
        # Delete all files from S3
        deleted_files = 0
        for document in documents:
            if document.s3_key:
                try:
                    s3_service.delete_file(document.s3_key)
                    deleted_files += 1
                    logger.info(f"Deleted S3 file: {document.s3_key}")
                except Exception as e:
                    logger.warning(f"Failed to delete S3 file {document.s3_key}: {str(e)}")
        
        # Delete submission (this will cascade delete all related records)
        # Including: documents, agency, policy, lines_of_business, contacts, 
        # nature_of_business, premises, prior_carriers, loss_history, signatures
        db.delete(submission)
        db.commit()
        
        logger.info(f"Deleted submission {submission_id} with {len(documents)} documents ({deleted_files} S3 files)")
        
        return {
            "message": "Submission deleted successfully",
            "submission_id": submission_id,
            "documents_deleted": len(documents),
            "s3_files_deleted": deleted_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete submission: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete submission: {str(e)}"
        )
