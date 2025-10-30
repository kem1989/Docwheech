"""
Enhanced ACORD 125 database models for Phase 2 enhancement
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, DECIMAL, Date, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database import Base


class BusinessStructureEnum(str, enum.Enum):
    """Business structure enumeration"""
    INDIVIDUAL = "INDIVIDUAL"
    PARTNERSHIP = "PARTNERSHIP"
    CORPORATION = "CORPORATION"
    LLC = "LLC"
    JOINT_VENTURE = "JOINT_VENTURE"
    NOT_FOR_PROFIT_ORG = "NOT_FOR_PROFIT_ORG"
    SUBCHAPTER_S_CORPORATION = "SUBCHAPTER_S_CORPORATION"
    TRUST = "TRUST"


class TransactionTypeEnum(str, enum.Enum):
    """Transaction type enumeration"""
    QUOTE = "QUOTE"
    RENEWAL = "RENEWAL"
    ISSUE_POLICY = "ISSUE_POLICY"
    BOUND = "BOUND"
    CANCEL = "CANCEL"
    CHANGE = "CHANGE"


class LineOfBusinessEnum(str, enum.Enum):
    """Line of business enumeration"""
    COMMERCIAL_GENERAL_LIABILITY = "COMMERCIAL_GENERAL_LIABILITY"
    COMMERCIAL_PROPERTY = "COMMERCIAL_PROPERTY"
    BUSINESS_AUTO = "BUSINESS_AUTO"
    UMBRELLA = "UMBRELLA"
    BUSINESS_OWNERS = "BUSINESS_OWNERS"
    GARAGE_AND_DEALERS = "GARAGE_AND_DEALERS"
    CRIME = "CRIME"
    BOILER_AND_MACHINERY = "BOILER_AND_MACHINERY"
    COMMERCIAL_INLAND_MARINE = "COMMERCIAL_INLAND_MARINE"
    CYBER_AND_PRIVACY = "CYBER_AND_PRIVACY"
    FIDUCIARY_LIABILITY = "FIDUCIARY_LIABILITY"
    LIQUOR_LIABILITY = "LIQUOR_LIABILITY"
    MOTOR_CARRIER = "MOTOR_CARRIER"
    TRUCKERS = "TRUCKERS"
    YACHT = "YACHT"


class InterestEnum(str, enum.Enum):
    """Property interest enumeration"""
    OWNER = "OWNER"
    TENANT = "TENANT"


class CarrierCategoryEnum(str, enum.Enum):
    """Prior carrier category enumeration"""
    GENERAL_LIABILITY = "GENERAL_LIABILITY"
    AUTOMOBILE = "AUTOMOBILE"
    PROPERTY = "PROPERTY"
    OTHER = "OTHER"


class Agency(Base):
    """Agency information model"""
    
    __tablename__ = "agencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Agency details
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    subcode = Column(String(50), nullable=True)
    agency_customer_id = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    contact_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    fax = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="agency")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "name": self.name,
            "code": self.code,
            "subcode": self.subcode,
            "agency_customer_id": self.agency_customer_id,
            "address": self.address,
            "contact_name": self.contact_name,
            "phone": self.phone,
            "fax": self.fax,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TransactionStatus(Base):
    """Transaction status model"""
    
    __tablename__ = "transaction_statuses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Transaction details
    type = Column(Enum(TransactionTypeEnum), nullable=False)
    bound_date = Column(Date, nullable=True)
    bound_time = Column(String(20), nullable=True)  # HH:MM AM/PM format
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="transaction_status")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "type": self.type.value if self.type else None,
            "bound_date": self.bound_date.isoformat() if self.bound_date else None,
            "bound_time": self.bound_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Policy(Base):
    """Policy information model"""
    
    __tablename__ = "policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Policy details
    proposed_effective_date = Column(Date, nullable=True)
    proposed_expiration_date = Column(Date, nullable=True)
    billing_plan = Column(String(100), nullable=True)
    payment_plan = Column(String(100), nullable=True)
    audit = Column(Boolean, default=False, nullable=False)
    deposit_premium = Column(DECIMAL(15, 2), nullable=True)
    minimum_premium = Column(DECIMAL(15, 2), nullable=True)
    method_of_payment = Column(String(50), nullable=True)  # DIRECT, AGENCY
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="policy")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "proposed_effective_date": self.proposed_effective_date.isoformat() if self.proposed_effective_date else None,
            "proposed_expiration_date": self.proposed_expiration_date.isoformat() if self.proposed_expiration_date else None,
            "billing_plan": self.billing_plan,
            "payment_plan": self.payment_plan,
            "audit": self.audit,
            "deposit_premium": float(self.deposit_premium) if self.deposit_premium else None,
            "minimum_premium": float(self.minimum_premium) if self.minimum_premium else None,
            "method_of_payment": self.method_of_payment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LineOfBusiness(Base):
    """Line of business model"""
    
    __tablename__ = "lines_of_business"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Line details
    line = Column(Enum(LineOfBusinessEnum), nullable=False)
    selected = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="lines_of_business")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "line": self.line.value if self.line else None,
            "selected": self.selected,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FirstNamedInsured(Base):
    """First named insured model"""
    
    __tablename__ = "first_named_insureds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Insured details
    name = Column(String(255), nullable=False)
    mailing_address = Column(Text, nullable=True)
    business_structure = Column(Enum(BusinessStructureEnum), nullable=True)
    number_of_members = Column(Integer, nullable=True)  # For LLC
    number_of_managers = Column(Integer, nullable=True)  # For LLC with managers
    naics_code = Column(String(10), nullable=True)
    sic_code = Column(String(10), nullable=True)
    gl_code = Column(String(10), nullable=True)
    fein_or_ssn = Column(String(20), nullable=True)
    business_phone = Column(String(50), nullable=True)
    website_address = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="first_named_insured")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "name": self.name,
            "mailing_address": self.mailing_address,
            "business_structure": self.business_structure.value if self.business_structure else None,
            "number_of_members": self.number_of_members,
            "number_of_managers": self.number_of_managers,
            "naics_code": self.naics_code,
            "sic_code": self.sic_code,
            "gl_code": self.gl_code,
            "fein_or_ssn": self.fein_or_ssn,
            "business_phone": self.business_phone,
            "website_address": self.website_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Contact(Base):
    """Contact information model"""
    
    __tablename__ = "contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Contact details
    contact_type = Column(String(100), nullable=True)
    contact_name = Column(String(255), nullable=True)
    primary_email = Column(String(255), nullable=True)
    secondary_email = Column(String(255), nullable=True)
    primary_phone = Column(String(50), nullable=True)
    primary_phone_type = Column(String(20), nullable=True)  # HOME, BUSINESS, CELL
    secondary_phone = Column(String(50), nullable=True)
    secondary_phone_type = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="contacts")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "contact_type": self.contact_type,
            "contact_name": self.contact_name,
            "primary_email": self.primary_email,
            "secondary_email": self.secondary_email,
            "primary_phone": self.primary_phone,
            "primary_phone_type": self.primary_phone_type,
            "secondary_phone": self.secondary_phone,
            "secondary_phone_type": self.secondary_phone_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NatureOfBusiness(Base):
    """Nature of business model"""
    
    __tablename__ = "nature_of_business"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Business details
    date_business_started = Column(Date, nullable=True)
    business_type = Column(Text, nullable=True)  # JSON array of business types
    description_of_primary_operations = Column(Text, nullable=True)
    retail_stores_or_service_operations = Column(Boolean, default=False, nullable=False)
    retail_percent_of_total_sales = Column(DECIMAL(5, 2), nullable=True)
    installation_service_repair_work = Column(Boolean, default=False, nullable=False)
    off_premises_installation_service_repair = Column(Boolean, default=False, nullable=False)
    description_of_operations_other_named_insureds = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="nature_of_business")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "date_business_started": self.date_business_started.isoformat() if self.date_business_started else None,
            "business_type": self.business_type,
            "description_of_primary_operations": self.description_of_primary_operations,
            "retail_stores_or_service_operations": self.retail_stores_or_service_operations,
            "retail_percent_of_total_sales": float(self.retail_percent_of_total_sales) if self.retail_percent_of_total_sales else None,
            "installation_service_repair_work": self.installation_service_repair_work,
            "off_premises_installation_service_repair": self.off_premises_installation_service_repair,
            "description_of_operations_other_named_insureds": self.description_of_operations_other_named_insureds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Premise(Base):
    """Premises information model"""
    
    __tablename__ = "premises"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Premise details
    location_number = Column(Integer, nullable=True)
    building_number = Column(Integer, nullable=True)
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    county = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip = Column(String(10), nullable=True)
    city_limits = Column(Boolean, default=False, nullable=False)
    description_of_operations = Column(Text, nullable=True)
    interest = Column(Enum(InterestEnum), nullable=True)
    owner_or_tenant_inside = Column(Boolean, default=False, nullable=False)
    owner_or_tenant_outside = Column(Boolean, default=False, nullable=False)
    number_full_time_employees = Column(Integer, nullable=True)
    number_part_time_employees = Column(Integer, nullable=True)
    annual_revenues = Column(DECIMAL(15, 2), nullable=True)
    occupied_area_sq_ft = Column(DECIMAL(10, 2), nullable=True)
    total_building_area_sq_ft = Column(DECIMAL(10, 2), nullable=True)
    open_to_public_area_sq_ft = Column(DECIMAL(10, 2), nullable=True)
    any_area_leased_to_others = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="premises")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "location_number": self.location_number,
            "building_number": self.building_number,
            "street_address": self.street_address,
            "city": self.city,
            "county": self.county,
            "state": self.state,
            "zip": self.zip,
            "city_limits": self.city_limits,
            "description_of_operations": self.description_of_operations,
            "interest": self.interest.value if self.interest else None,
            "owner_or_tenant_inside": self.owner_or_tenant_inside,
            "owner_or_tenant_outside": self.owner_or_tenant_outside,
            "number_full_time_employees": self.number_full_time_employees,
            "number_part_time_employees": self.number_part_time_employees,
            "annual_revenues": float(self.annual_revenues) if self.annual_revenues else None,
            "occupied_area_sq_ft": float(self.occupied_area_sq_ft) if self.occupied_area_sq_ft else None,
            "total_building_area_sq_ft": float(self.total_building_area_sq_ft) if self.total_building_area_sq_ft else None,
            "open_to_public_area_sq_ft": float(self.open_to_public_area_sq_ft) if self.open_to_public_area_sq_ft else None,
            "any_area_leased_to_others": self.any_area_leased_to_others,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PriorCarrier(Base):
    """Prior carrier information model"""
    
    __tablename__ = "prior_carriers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Carrier details
    category = Column(Enum(CarrierCategoryEnum), nullable=True)
    carrier_name = Column(String(255), nullable=True)
    policy_number = Column(String(100), nullable=True)
    effective_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True)
    premium = Column(DECIMAL(10, 2), nullable=True)
    years_with_carrier = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="prior_carriers")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "category": self.category.value if self.category else None,
            "carrier_name": self.carrier_name,
            "policy_number": self.policy_number,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "premium": float(self.premium) if self.premium else None,
            "years_with_carrier": self.years_with_carrier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LossHistory(Base):
    """Loss history model"""
    
    __tablename__ = "loss_histories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Loss history details
    has_losses = Column(Boolean, default=False, nullable=False)
    total_losses_amount = Column(DECIMAL(15, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="loss_history")
    losses = relationship("Loss", back_populates="loss_history", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "has_losses": self.has_losses,
            "total_losses_amount": float(self.total_losses_amount) if self.total_losses_amount else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Loss(Base):
    """Individual loss model"""
    
    __tablename__ = "losses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loss_history_id = Column(UUID(as_uuid=True), ForeignKey("loss_histories.id"), nullable=False, index=True)
    
    # Loss details
    date_of_loss = Column(Date, nullable=True)
    line_type = Column(String(50), nullable=True)
    description_of_occurrence = Column(Text, nullable=True)
    amount_paid = Column(DECIMAL(10, 2), nullable=True)
    amount_reserved = Column(DECIMAL(10, 2), nullable=True)
    claim_open = Column(Boolean, default=False, nullable=False)
    subrogation = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    loss_history = relationship("LossHistory", back_populates="losses")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "loss_history_id": str(self.loss_history_id),
            "date_of_loss": self.date_of_loss.isoformat() if self.date_of_loss else None,
            "line_type": self.line_type,
            "description_of_occurrence": self.description_of_occurrence,
            "amount_paid": float(self.amount_paid) if self.amount_paid else None,
            "amount_reserved": float(self.amount_reserved) if self.amount_reserved else None,
            "claim_open": self.claim_open,
            "subrogation": self.subrogation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Signature(Base):
    """Signature model"""
    
    __tablename__ = "signatures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True)
    
    # Signature details
    signature_type = Column(String(50), nullable=False)  # applicant, producer
    signature_data = Column(Text, nullable=True)  # Digital signature or image
    signer_name = Column(String(255), nullable=True)  # For producer
    signature_date = Column(Date, nullable=True)
    state_producer_license_number = Column(String(100), nullable=True)  # For producer
    national_producer_number = Column(String(100), nullable=True)  # For producer
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="signatures")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "submission_id": str(self.submission_id),
            "signature_type": self.signature_type,
            "signature_data": self.signature_data,
            "signer_name": self.signer_name,
            "signature_date": self.signature_date.isoformat() if self.signature_date else None,
            "state_producer_license_number": self.state_producer_license_number,
            "national_producer_number": self.national_producer_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

