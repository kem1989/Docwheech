"""
Database service for AI extraction results
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException

from app.database import get_db
from app.models.submission import Submission
from app.models.document import Document
from app.models.acord_125 import (
    Agency,
    TransactionStatus,
    Policy,
    LineOfBusiness,
    FirstNamedInsured,
    OtherNamedInsured,
    Contact,
    NatureOfBusiness,
    Premise,
    PriorCarrier,
    LossHistory,
    Loss,
    Signature,
    BusinessStructureEnum,
    TransactionTypeEnum,
    LineOfBusinessEnum,
    InterestEnum,
    CarrierCategoryEnum,
)
from app.utils.data_transformer import transform_extracted_to_acord_schema

logger = logging.getLogger(__name__)


class ExtractionDatabaseService:
    """Service for managing AI extraction results in database"""
    
    def __init__(self, db: Session):
        """Initialize with database session"""
        self.db = db
    
    def create_extraction_job(
        self, 
        submission_id: str, 
        user_id: str, 
        document_keys: List[str],
        confidence_threshold: float = 0.7
    ) -> Submission:
        """
        Create a new extraction job in the database
        
        Args:
            submission_id: Unique submission identifier
            user_id: User identifier
            document_keys: List of document S3 keys
            confidence_threshold: Confidence threshold for extraction
            
        Returns:
            Submission object
        """
        try:
            # Check if submission already exists
            submission = self.db.query(Submission).filter(
                and_(
                    Submission.id == submission_id,
                    Submission.user_id == user_id
                )
            ).first()
            
            if not submission:
                # Create new submission
                submission = Submission(
                    id=submission_id,
                    user_id=user_id,
                    status="processing",
                    extraction_status="processing",
                    extraction_progress=0,
                    total_files=len(document_keys),
                    processed_files=0
                )
                self.db.add(submission)
            else:
                # Update existing submission
                submission.status = "processing"
                submission.extraction_status = "processing"
                submission.extraction_progress = 0
                submission.extraction_error = None
                submission.total_files = len(document_keys)
                submission.processed_files = 0
            
            self.db.commit()
            logger.info(f"Created extraction job for submission {submission_id}")
            return submission
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create extraction job: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create extraction job: {str(e)}")
    
    def update_extraction_progress(
        self, 
        submission_id: str, 
        progress: int, 
        status: str = "processing"
    ) -> bool:
        """
        Update extraction progress
        
        Args:
            submission_id: Submission identifier
            progress: Progress percentage (0-100)
            status: Extraction status
            
        Returns:
            True if successful
        """
        try:
            submission = self.db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if not submission:
                logger.error(f"Submission {submission_id} not found")
                return False
            
            submission.extraction_progress = min(100, max(0, progress))
            submission.extraction_status = status
            
            if progress >= 100:
                submission.extraction_status = "completed"
                submission.status = "completed"
            
            self.db.commit()
            logger.info(f"Updated extraction progress for {submission_id}: {progress}%")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update extraction progress: {str(e)}")
            return False
    
    def save_extraction_results(
        self, 
        submission_id: str, 
        extraction_result: Dict[str, Any]
    ) -> bool:
        """
        Save AI extraction results to database
        
        Args:
            submission_id: Submission identifier
            extraction_result: Complete extraction result
            
        Returns:
            True if successful
        """
        try:
            submission = self.db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if not submission:
                logger.error(f"Submission {submission_id} not found")
                return False
            
            # Get extracted data with confidence wrappers (for audit/review)
            extracted_data = extraction_result.get('extracted_data')
            
            # Transform extracted data to ACORD-compliant schema (unwrap confidence objects)
            logger.info("Transforming extracted data to ACORD schema format")
            acord_data = transform_extracted_to_acord_schema(extracted_data)
            
            # Add risk narrative to ACORD data
            if 'risk_narrative' in extraction_result:
                acord_data['risk_narrative'] = extraction_result['risk_narrative']
            
            # Update submission with extraction results
            submission.extracted_data = extracted_data  # Keep confidence wrappers for review
            submission.acord_data = acord_data  # Clean ACORD-compliant data
            submission.extraction_status = "completed"
            submission.extraction_progress = 100
            submission.status = "completed"
            submission.processed_files = extraction_result.get('processing_stats', {}).get('total_documents', 0)
            
            # Add completion timestamp
            from datetime import datetime
            submission.completed_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Saved extraction results for submission {submission_id}")
            logger.info(f"Transformed ACORD data: {len(acord_data)} top-level fields")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save extraction results: {str(e)}", exc_info=True)
            return False
    
    def save_extraction_error(
        self, 
        submission_id: str, 
        error_message: str
    ) -> bool:
        """
        Save extraction error to database
        
        Args:
            submission_id: Submission identifier
            error_message: Error message
            
        Returns:
            True if successful
        """
        try:
            submission = self.db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if not submission:
                logger.error(f"Submission {submission_id} not found")
                return False
            
            submission.extraction_status = "failed"
            submission.extraction_error = error_message
            submission.status = "failed"
            
            self.db.commit()
            logger.info(f"Saved extraction error for submission {submission_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save extraction error: {str(e)}")
            return False
    
    def get_extraction_status(
        self, 
        submission_id: str, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get extraction status for a submission
        
        Args:
            submission_id: Submission identifier
            user_id: User identifier
            
        Returns:
            Status information or None
        """
        try:
            submission = self.db.query(Submission).filter(
                and_(
                    Submission.id == submission_id,
                    Submission.user_id == user_id
                )
            ).first()
            
            if not submission:
                return None
            
            return {
                "submission_id": str(submission.id),
                "status": submission.status,
                "extraction_status": submission.extraction_status,
                "extraction_progress": submission.extraction_progress,
                "extraction_error": submission.extraction_error,
                "total_files": submission.total_files,
                "processed_files": submission.processed_files,
                "created_at": submission.created_at.isoformat() if submission.created_at else None,
                "updated_at": submission.updated_at.isoformat() if submission.updated_at else None,
                "completed_at": submission.completed_at.isoformat() if submission.completed_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get extraction status: {str(e)}")
            return None
    
    def get_extraction_results(
        self, 
        submission_id: str, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete extraction results
        
        Args:
            submission_id: Submission identifier
            user_id: User identifier
            
        Returns:
            Complete extraction results or None
        """
        try:
            submission = self.db.query(Submission).filter(
                and_(
                    Submission.id == submission_id,
                    Submission.user_id == user_id
                )
            ).first()
            
            if not submission:
                return None
            
            if submission.extraction_status != "completed":
                return {
                    "submission_id": str(submission.id),
                    "status": submission.extraction_status,
                    "message": "Extraction not completed yet"
                }
            
            # Extract processing stats from extracted_data if available
            processing_stats = {
                "total_documents": submission.total_files,
                "processed_documents": submission.processed_files,
                "completion_percentage": submission.extraction_progress,
                "total_pages": 0,
                "average_confidence": 0.0,
                "extraction_method": "openai_gpt4_textract",
                "missing_fields": []
            }
            
            # Try to get more detailed stats from extracted_data
            if submission.extracted_data and isinstance(submission.extracted_data, dict):
                if "processing_stats" in submission.extracted_data:
                    processing_stats.update(submission.extracted_data["processing_stats"])
            
            # Extract risk narrative from extracted_data if available
            risk_narrative = ""
            if submission.extracted_data and isinstance(submission.extracted_data, dict):
                risk_narrative = submission.extracted_data.get("risk_narrative", "")
            
            return {
                "extraction_id": str(submission.id),
                "submission_id": str(submission.id),
                "status": submission.status,
                "extracted_data": submission.extracted_data,
                "acord_schema": submission.acord_data,
                "risk_narrative": risk_narrative,
                "extraction_timestamp": submission.completed_at.isoformat() if submission.completed_at else None,
                "processing_stats": processing_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get extraction results: {str(e)}")
            return None
    
    def list_user_extractions(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List user's extraction jobs
        
        Args:
            user_id: User identifier
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of extraction jobs
        """
        try:
            submissions = self.db.query(Submission).filter(
                Submission.user_id == user_id
            ).order_by(Submission.created_at.desc()).offset(offset).limit(limit).all()
            
            return [submission.to_dict() for submission in submissions]
            
        except Exception as e:
            logger.error(f"Failed to list user extractions: {str(e)}")
            return []
    
    def cleanup_failed_extractions(self, days_old: int = 7) -> int:
        """
        Clean up failed extractions older than specified days
        
        Args:
            days_old: Number of days to keep failed extractions
            
        Returns:
            Number of cleaned up extractions
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            failed_submissions = self.db.query(Submission).filter(
                and_(
                    Submission.extraction_status == "failed",
                    Submission.created_at < cutoff_date
                )
            ).all()
            
            count = len(failed_submissions)
            
            for submission in failed_submissions:
                self.db.delete(submission)
            
            self.db.commit()
            logger.info(f"Cleaned up {count} failed extractions")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to cleanup failed extractions: {str(e)}")
            return 0
    
    def save_enhanced_acord_data(self, submission_id: str, acord_data: Dict[str, Any]) -> bool:
        """
        Save enhanced ACORD data to the new schema tables
        
        Args:
            submission_id: Submission identifier
            acord_data: Enhanced ACORD data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the submission
            submission = self.db.query(Submission).filter(Submission.id == submission_id).first()
            if not submission:
                logger.error(f"Submission {submission_id} not found")
                return False
            
            # Save Agency data
            if "agency" in acord_data:
                agency_data = acord_data["agency"]
                agency = Agency(
                    submission_id=submission_id,
                    name=agency_data.get("name"),
                    code=agency_data.get("code"),
                    subcode=agency_data.get("subcode"),
                    agency_customer_id=agency_data.get("agency_customer_id"),
                    address=agency_data.get("address"),
                    contact_name=agency_data.get("contact_name"),
                    phone=agency_data.get("phone"),
                    fax=agency_data.get("fax"),
                    email=agency_data.get("email")
                )
                self.db.add(agency)
            
            # Save Transaction Status
            if "transaction_status" in acord_data:
                tx_data = acord_data["transaction_status"]
                transaction_status = TransactionStatus(
                    submission_id=submission_id,
                    type=TransactionTypeEnum(tx_data.get("type")) if tx_data.get("type") else None,
                    bound_date=tx_data.get("bound_date"),
                    bound_time=tx_data.get("bound_time")
                )
                self.db.add(transaction_status)
            
            # Save Policy data
            if "policy" in acord_data:
                policy_data = acord_data["policy"]
                policy = Policy(
                    submission_id=submission_id,
                    proposed_effective_date=policy_data.get("proposed_effective_date"),
                    proposed_expiration_date=policy_data.get("proposed_expiration_date"),
                    billing_plan=policy_data.get("billing_plan"),
                    payment_plan=policy_data.get("payment_plan"),
                    audit=policy_data.get("audit", False),
                    deposit_premium=policy_data.get("deposit_premium"),
                    minimum_premium=policy_data.get("minimum_premium"),
                    method_of_payment=policy_data.get("method_of_payment")
                )
                self.db.add(policy)
            
            # Save Lines of Business
            if "lines_of_business" in acord_data:
                for lob_data in acord_data["lines_of_business"]:
                    line_of_business = LineOfBusiness(
                        submission_id=submission_id,
                        line=LineOfBusinessEnum(lob_data.get("line")) if lob_data.get("line") else None,
                        selected=lob_data.get("selected", False)
                    )
                    self.db.add(line_of_business)
            
            # Save First Named Insured
            if "first_named_insured" in acord_data:
                fni_data = acord_data["first_named_insured"]
                first_named_insured = FirstNamedInsured(
                    submission_id=submission_id,
                    name=fni_data.get("name"),
                    mailing_address=fni_data.get("mailing_address"),
                    business_structure=BusinessStructureEnum(fni_data.get("business_structure")) if fni_data.get("business_structure") else None,
                    number_of_members=fni_data.get("number_of_members"),
                    number_of_managers=fni_data.get("number_of_managers"),
                    naics_code=fni_data.get("naics_code"),
                    sic_code=fni_data.get("sic_code"),
                    gl_code=fni_data.get("gl_code"),
                    fein_or_ssn=fni_data.get("fein_or_ssn"),
                    business_phone=fni_data.get("business_phone"),
                    website_address=fni_data.get("website_address")
                )
                self.db.add(first_named_insured)
            
            # Save Other Named Insureds
            if "other_named_insureds" in acord_data:
                for oni_data in acord_data["other_named_insureds"]:
                    other_named_insured = OtherNamedInsured(
                        submission_id=submission_id,
                        name=oni_data.get("name"),
                        mailing_address=oni_data.get("mailing_address"),
                        business_structure=BusinessStructureEnum(oni_data.get("business_structure")) if oni_data.get("business_structure") else None,
                        number_of_members=oni_data.get("number_of_members"),
                        number_of_managers=oni_data.get("number_of_managers"),
                        naics_code=oni_data.get("naics_code"),
                        sic_code=oni_data.get("sic_code"),
                        gl_code=oni_data.get("gl_code"),
                        fein_or_ssn=oni_data.get("fein_or_ssn"),
                        business_phone=oni_data.get("business_phone"),
                        website_address=oni_data.get("website_address"),
                    )
                    self.db.add(other_named_insured)
            
            # Save Contacts
            if "contacts" in acord_data:
                for contact_data in acord_data["contacts"]:
                    contact = Contact(
                        submission_id=submission_id,
                        contact_type=contact_data.get("contact_type"),
                        contact_name=contact_data.get("contact_name"),
                        primary_email=contact_data.get("primary_email"),
                        secondary_email=contact_data.get("secondary_email"),
                        primary_phone=contact_data.get("primary_phone"),
                        primary_phone_type=contact_data.get("primary_phone_type"),
                        secondary_phone=contact_data.get("secondary_phone"),
                        secondary_phone_type=contact_data.get("secondary_phone_type")
                    )
                    self.db.add(contact)
            
            # Save Nature of Business
            if "nature_of_business" in acord_data:
                nob_data = acord_data["nature_of_business"]
                nature_of_business = NatureOfBusiness(
                    submission_id=submission_id,
                    date_business_started=nob_data.get("date_business_started"),
                    business_type=nob_data.get("business_type"),
                    description_of_primary_operations=nob_data.get("description_of_primary_operations"),
                    retail_stores_or_service_operations=nob_data.get("retail_stores_or_service_operations", False),
                    retail_percent_of_total_sales=nob_data.get("retail_percent_of_total_sales"),
                    installation_service_repair_work=nob_data.get("installation_service_repair_work", False),
                    off_premises_installation_service_repair=nob_data.get("off_premises_installation_service_repair", False),
                    description_of_operations_other_named_insureds=nob_data.get("description_of_operations_other_named_insureds")
                )
                self.db.add(nature_of_business)
            
            # Save Premises
            if "premises" in acord_data:
                for premise_data in acord_data["premises"]:
                    premise = Premise(
                        submission_id=submission_id,
                        location_number=premise_data.get("location_number"),
                        building_number=premise_data.get("building_number"),
                        street_address=premise_data.get("street_address"),
                        city=premise_data.get("city"),
                        county=premise_data.get("county"),
                        state=premise_data.get("state"),
                        zip=premise_data.get("zip"),
                        city_limits=premise_data.get("city_limits", False),
                        description_of_operations=premise_data.get("description_of_operations"),
                        interest=InterestEnum(premise_data.get("interest")) if premise_data.get("interest") else None,
                        owner_or_tenant_inside=premise_data.get("owner_or_tenant_inside", False),
                        owner_or_tenant_outside=premise_data.get("owner_or_tenant_outside", False),
                        number_full_time_employees=premise_data.get("number_full_time_employees"),
                        number_part_time_employees=premise_data.get("number_part_time_employees"),
                        annual_revenues=premise_data.get("annual_revenues"),
                        occupied_area_sq_ft=premise_data.get("occupied_area_sq_ft"),
                        total_building_area_sq_ft=premise_data.get("total_building_area_sq_ft"),
                        open_to_public_area_sq_ft=premise_data.get("open_to_public_area_sq_ft"),
                        any_area_leased_to_others=premise_data.get("any_area_leased_to_others", False)
                    )
                    self.db.add(premise)
            
            # Save Prior Carriers
            if "prior_carriers" in acord_data:
                for carrier_data in acord_data["prior_carriers"]:
                    prior_carrier = PriorCarrier(
                        submission_id=submission_id,
                        category=CarrierCategoryEnum(carrier_data.get("category")) if carrier_data.get("category") else None,
                        carrier_name=carrier_data.get("carrier_name"),
                        policy_number=carrier_data.get("policy_number"),
                        effective_date=carrier_data.get("effective_date"),
                        expiration_date=carrier_data.get("expiration_date"),
                        premium=carrier_data.get("premium"),
                        years_with_carrier=carrier_data.get("years_with_carrier")
                    )
                    self.db.add(prior_carrier)
            
            # Save Loss History
            if "loss_history" in acord_data:
                loss_data = acord_data["loss_history"]
                loss_history = LossHistory(
                    submission_id=submission_id,
                    has_losses=loss_data.get("has_losses", False),
                    total_losses_amount=loss_data.get("total_losses_amount")
                )
                self.db.add(loss_history)
                self.db.flush()  # Get the ID
                
                # Save individual losses
                if "losses" in loss_data:
                    for loss_item in loss_data["losses"]:
                        loss = Loss(
                            loss_history_id=loss_history.id,
                            date_of_loss=loss_item.get("date_of_loss"),
                            line_type=loss_item.get("line_type"),
                            description_of_occurrence=loss_item.get("description_of_occurrence"),
                            amount_paid=loss_item.get("amount_paid"),
                            amount_reserved=loss_item.get("amount_reserved"),
                            claim_open=loss_item.get("claim_open", False),
                            subrogation=loss_item.get("subrogation", False)
                        )
                        self.db.add(loss)
            
            # Save Signatures
            if "signatures" in acord_data:
                for sig_data in acord_data["signatures"]:
                    signature = Signature(
                        submission_id=submission_id,
                        signature_type=sig_data.get("signature_type"),
                        signature_data=sig_data.get("signature_data"),
                        signer_name=sig_data.get("signer_name"),
                        signature_date=sig_data.get("signature_date"),
                        state_producer_license_number=sig_data.get("state_producer_license_number"),
                        national_producer_number=sig_data.get("national_producer_number")
                    )
                    self.db.add(signature)
            
            self.db.commit()
            logger.info(f"Successfully saved enhanced ACORD data for submission {submission_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save enhanced ACORD data: {str(e)}")
            return False
    
    def get_enhanced_acord_data(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """
        Get enhanced ACORD data from the new schema tables
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            Enhanced ACORD data dictionary or None if not found
        """
        try:
            submission = self.db.query(Submission).filter(Submission.id == submission_id).first()
            if not submission:
                return None
            
            result = {
                "submission_id": str(submission.id),
                "status": submission.status,
                "extraction_status": submission.extraction_status,
                "created_at": submission.created_at.isoformat() if submission.created_at else None,
                "updated_at": submission.updated_at.isoformat() if submission.updated_at else None,
            }
            
            # Get Agency data
            agency = self.db.query(Agency).filter(Agency.submission_id == submission_id).first()
            if agency:
                result["agency"] = agency.to_dict()
            
            # Get Transaction Status
            tx_status = self.db.query(TransactionStatus).filter(TransactionStatus.submission_id == submission_id).first()
            if tx_status:
                result["transaction_status"] = tx_status.to_dict()
            
            # Get Policy data
            policy = self.db.query(Policy).filter(Policy.submission_id == submission_id).first()
            if policy:
                result["policy"] = policy.to_dict()
            
            # Get Lines of Business
            lines_of_business = self.db.query(LineOfBusiness).filter(LineOfBusiness.submission_id == submission_id).all()
            if lines_of_business:
                result["lines_of_business"] = [lob.to_dict() for lob in lines_of_business]
            
            # Get First Named Insured
            fni = self.db.query(FirstNamedInsured).filter(FirstNamedInsured.submission_id == submission_id).first()
            if fni:
                result["first_named_insured"] = fni.to_dict()
            
            other_named_insureds = self.db.query(OtherNamedInsured).filter(OtherNamedInsured.submission_id == submission_id).all()
            if other_named_insureds:
                result["other_named_insureds"] = [oni.to_dict() for oni in other_named_insureds]
            
            # Get Contacts
            contacts = self.db.query(Contact).filter(Contact.submission_id == submission_id).all()
            if contacts:
                result["contacts"] = [contact.to_dict() for contact in contacts]
            
            # Get Nature of Business
            nob = self.db.query(NatureOfBusiness).filter(NatureOfBusiness.submission_id == submission_id).first()
            if nob:
                result["nature_of_business"] = nob.to_dict()
            
            # Get Premises
            premises = self.db.query(Premise).filter(Premise.submission_id == submission_id).all()
            if premises:
                result["premises"] = [premise.to_dict() for premise in premises]
            
            # Get Prior Carriers
            prior_carriers = self.db.query(PriorCarrier).filter(PriorCarrier.submission_id == submission_id).all()
            if prior_carriers:
                result["prior_carriers"] = [carrier.to_dict() for carrier in prior_carriers]
            
            # Get Loss History
            loss_history = self.db.query(LossHistory).filter(LossHistory.submission_id == submission_id).first()
            if loss_history:
                loss_history_dict = loss_history.to_dict()
                losses = self.db.query(Loss).filter(Loss.loss_history_id == loss_history.id).all()
                if losses:
                    loss_history_dict["losses"] = [loss.to_dict() for loss in losses]
                result["loss_history"] = loss_history_dict
            
            # Get Signatures
            signatures = self.db.query(Signature).filter(Signature.submission_id == submission_id).all()
            if signatures:
                result["signatures"] = [sig.to_dict() for sig in signatures]
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get enhanced ACORD data: {str(e)}")
            return None
    
    # =========================================================================
    # FIELD EDITING METHODS
    # =========================================================================
    
    def get_field_value(
        self,
        submission_id: str,
        field_path: str
    ) -> Any:
        """
        Get the current value of a specific field from extracted data.
        
        Args:
            submission_id: Submission identifier
            field_path: Dot-notation path to the field (e.g., "first_named_insured.name")
            
        Returns:
            Current field value or None
        """
        try:
            submission = self.db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if not submission or not submission.extracted_data:
                return None
            
            # Navigate the field path
            value = submission.extracted_data
            for key in field_path.split('.'):
                # Handle array indices like "premises[0]"
                if '[' in key:
                    base_key = key.split('[')[0]
                    index = int(key.split('[')[1].rstrip(']'))
                    if isinstance(value, dict) and base_key in value:
                        value = value[base_key]
                        if isinstance(value, list) and index < len(value):
                            value = value[index]
                        else:
                            return None
                    else:
                        return None
                elif isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            # Unwrap confidence wrapper if present
            if isinstance(value, dict) and 'value' in value:
                return value.get('value')
            return value
            
        except Exception as e:
            logger.error(f"Failed to get field value: {str(e)}")
            return None
    
    def update_extracted_field(
        self,
        submission_id: str,
        field_path: str,
        new_value: Any,
        user_id: str
    ) -> bool:
        """
        Update a single field in the extracted data.
        
        Args:
            submission_id: Submission identifier
            field_path: Dot-notation path to the field
            new_value: New value for the field
            user_id: User making the edit
            
        Returns:
            True if successful
        """
        try:
            submission = self.db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if not submission:
                logger.error(f"Submission {submission_id} not found")
                return False
            
            # Get old value for history
            old_value = self.get_field_value(submission_id, field_path)
            
            # Update extracted_data (with confidence wrappers)
            if submission.extracted_data:
                extracted_data = dict(submission.extracted_data)
                self._set_nested_value(extracted_data, field_path, {
                    'value': new_value,
                    'confidence': 1.0,  # Manual edits have 100% confidence
                    'validation_status': 'validated',
                    'edited': True,
                    'original_value': old_value
                })
                submission.extracted_data = extracted_data
            
            # Update acord_data (clean values)
            if submission.acord_data:
                acord_data = dict(submission.acord_data)
                self._set_nested_value(acord_data, field_path, new_value)
                submission.acord_data = acord_data
            
            # Update edit history
            self._add_edit_history(
                submission_id=submission_id,
                field_path=field_path,
                old_value=old_value,
                new_value=new_value,
                user_id=user_id
            )
            
            # Update timestamp
            from datetime import datetime
            submission.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Updated field {field_path} for submission {submission_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update field: {str(e)}", exc_info=True)
            return False
    
    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any) -> None:
        """
        Set a value at a nested path in a dictionary.
        
        Args:
            data: Dictionary to modify
            field_path: Dot-notation path
            value: Value to set
        """
        keys = field_path.split('.')
        current = data
        
        for i, key in enumerate(keys[:-1]):
            # Handle array indices
            if '[' in key:
                base_key = key.split('[')[0]
                index = int(key.split('[')[1].rstrip(']'))
                
                if base_key not in current:
                    current[base_key] = []
                
                while len(current[base_key]) <= index:
                    current[base_key].append({})
                
                current = current[base_key][index]
            else:
                if key not in current:
                    current[key] = {}
                current = current[key]
        
        # Set the final value
        final_key = keys[-1]
        if '[' in final_key:
            base_key = final_key.split('[')[0]
            index = int(final_key.split('[')[1].rstrip(']'))
            
            if base_key not in current:
                current[base_key] = []
            
            while len(current[base_key]) <= index:
                current[base_key].append(None)
            
            current[base_key][index] = value
        else:
            current[final_key] = value
    
    def _add_edit_history(
        self,
        submission_id: str,
        field_path: str,
        old_value: Any,
        new_value: Any,
        user_id: str
    ) -> None:
        """
        Add an entry to the edit history.
        
        Note: This stores edit history in the submission's metadata.
        For production, consider using a separate EditHistory table.
        """
        from datetime import datetime
        
        submission = self.db.query(Submission).filter(
            Submission.id == submission_id
        ).first()
        
        if not submission:
            return
        
        # Get existing edit history or create new
        edit_history = submission.edit_history or []
        
        # Add new entry
        edit_history.append({
            'field_path': field_path,
            'old_value': old_value,
            'new_value': new_value,
            'edited_at': datetime.utcnow().isoformat(),
            'edited_by': user_id
        })
        
        submission.edit_history = edit_history
    
    def get_edit_history(self, submission_id: str) -> List[Dict[str, Any]]:
        """
        Get the edit history for a submission.
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            List of edit history entries
        """
        try:
            submission = self.db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if not submission:
                return []
            
            return submission.edit_history or []
            
        except Exception as e:
            logger.error(f"Failed to get edit history: {str(e)}")
            return []