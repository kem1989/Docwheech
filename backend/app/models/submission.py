"""
Submission database model
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Submission(Base):
    """Submission model for tracking insurance application submissions"""
    
    __tablename__ = "submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Submission metadata
    title = Column(String(255), nullable=True)
    status = Column(String(50), default="draft", nullable=False, index=True)  # draft, processing, completed, failed
    submission_type = Column(String(50), default="acord_125", nullable=False)  # acord_125, custom, etc.
    
    # ACORD data
    acord_data = Column(JSON, nullable=True)  # Structured ACORD 125 data
    extracted_data = Column(JSON, nullable=True)  # Raw extracted data before ACORD conversion
    general_questions = Column(JSON, nullable=True)  # Manual responses for ACORD general questions
    edit_history = Column(JSON, nullable=True, default=list)  # Track field edits for audit
    
    # Processing status
    extraction_status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    extraction_progress = Column(Integer, default=0, nullable=False)  # 0-100
    extraction_error = Column(Text, nullable=True)
    
    # File management
    total_files = Column(Integer, default=0, nullable=False)
    processed_files = Column(Integer, default=0, nullable=False)
    
    # Gap analysis
    gap_analysis_results = Column(JSON, nullable=True)  # Stored gap analysis report
    gap_analysis_timestamp = Column(DateTime(timezone=True), nullable=True)  # When analysis was last run
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="submissions")
    documents = relationship("Document", back_populates="submission", cascade="all, delete-orphan")
    
    # Enhanced ACORD 125 relationships
    agency = relationship("Agency", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    transaction_status = relationship("TransactionStatus", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    policy = relationship("Policy", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    lines_of_business = relationship("LineOfBusiness", back_populates="submission", cascade="all, delete-orphan")
    first_named_insured = relationship("FirstNamedInsured", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    other_named_insureds = relationship("OtherNamedInsured", back_populates="submission", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="submission", cascade="all, delete-orphan")
    nature_of_business = relationship("NatureOfBusiness", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    premises = relationship("Premise", back_populates="submission", cascade="all, delete-orphan")
    prior_carriers = relationship("PriorCarrier", back_populates="submission", cascade="all, delete-orphan")
    loss_history = relationship("LossHistory", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    signatures = relationship("Signature", back_populates="submission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Submission(id={self.id}, user_id={self.user_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert submission to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "status": self.status,
            "submission_type": self.submission_type,
            "acord_data": self.acord_data,
            "extracted_data": self.extracted_data,
            "general_questions": self.general_questions,
            "edit_history": self.edit_history,
            "extraction_status": self.extraction_status,
            "extraction_progress": self.extraction_progress,
            "extraction_error": self.extraction_error,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "gap_analysis_results": self.gap_analysis_results,
            "gap_analysis_timestamp": self.gap_analysis_timestamp.isoformat() if self.gap_analysis_timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

