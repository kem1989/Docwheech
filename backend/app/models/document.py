"""
Document database model
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Document(Base):
    """Document model for tracking uploaded files"""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # File metadata
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, xlsx, jpg, png, etc.
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    
    # Storage information
    s3_bucket = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)  # S3 object key
    s3_url = Column(Text, nullable=True)  # Pre-signed URL for access
    
    # Processing status
    processing_status = Column(String(50), default="uploaded", nullable=False)  # uploaded, processing, completed, failed
    extraction_data = Column(Text, nullable=True)  # JSON string of extracted data
    extraction_confidence = Column(Integer, nullable=True)  # 0-100 confidence score
    extraction_error = Column(Text, nullable=True)
    
    # File validation
    is_valid = Column(Boolean, default=True, nullable=False)
    validation_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    submission = relationship("Submission", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.original_filename}, type={self.file_type})>"
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "s3_bucket": self.s3_bucket,
            "s3_key": self.s3_key,
            "s3_url": self.s3_url,
            "processing_status": self.processing_status,
            "extraction_data": self.extraction_data,
            "extraction_confidence": self.extraction_confidence,
            "extraction_error": self.extraction_error,
            "is_valid": self.is_valid,
            "validation_error": self.validation_error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }

