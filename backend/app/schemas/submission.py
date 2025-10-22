"""
Pydantic schemas for submission-related requests and responses
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, UUID4
from enum import Enum


class SubmissionStatus(str, Enum):
    """Submission status enumeration"""
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractionStatus(str, Enum):
    """Extraction status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SubmissionType(str, Enum):
    """Submission type enumeration"""
    ACORD_125 = "acord_125"
    CUSTOM = "custom"


class SubmissionBase(BaseModel):
    """Base submission schema"""
    title: Optional[str] = None
    submission_type: SubmissionType = SubmissionType.ACORD_125


class SubmissionCreate(SubmissionBase):
    """Schema for creating a new submission"""
    pass


class SubmissionUpdate(BaseModel):
    """Schema for updating a submission"""
    title: Optional[str] = None
    status: Optional[SubmissionStatus] = None
    acord_data: Optional[Dict[str, Any]] = None
    extracted_data: Optional[Dict[str, Any]] = None
    extraction_status: Optional[ExtractionStatus] = None
    extraction_progress: Optional[int] = Field(None, ge=0, le=100)
    extraction_error: Optional[str] = None


class SubmissionResponse(SubmissionBase):
    """Schema for submission response"""
    id: UUID4
    user_id: UUID4
    status: SubmissionStatus
    acord_data: Optional[Dict[str, Any]] = None
    extracted_data: Optional[Dict[str, Any]] = None
    extraction_status: ExtractionStatus
    extraction_progress: int = Field(ge=0, le=100)
    extraction_error: Optional[str] = None
    total_files: int
    processed_files: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubmissionListResponse(BaseModel):
    """Schema for submission list response"""
    submissions: List[SubmissionResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class FileUploadRequest(BaseModel):
    """Schema for file upload request"""
    submission_id: UUID4
    files: List[str] = Field(..., description="List of file names to upload")


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    submission_id: UUID4
    upload_urls: Dict[str, Dict[str, Any]] = Field(..., description="File name to upload URL mapping")
    expires_in: int = Field(..., description="Upload URL expiration time in seconds")


class FileInfo(BaseModel):
    """Schema for file information"""
    filename: str
    file_type: str
    size: int
    is_valid: bool
    error: Optional[str] = None
    mime_type: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: UUID4
    submission_id: UUID4
    original_filename: str
    file_type: str
    file_size: int
    mime_type: str
    s3_bucket: str
    s3_key: str
    s3_url: Optional[str] = None
    processing_status: str
    extraction_data: Optional[str] = None
    extraction_confidence: Optional[int] = None
    extraction_error: Optional[str] = None
    is_valid: bool
    validation_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list response"""
    documents: List[DocumentResponse]
    total: int
    submission_id: UUID4


class SubmissionSummary(BaseModel):
    """Schema for submission summary"""
    id: UUID4
    title: Optional[str]
    status: SubmissionStatus
    submission_type: SubmissionType
    total_files: int
    processed_files: int
    extraction_status: ExtractionStatus
    extraction_progress: int
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentResponse] = []
    
    class Config:
        from_attributes = True



