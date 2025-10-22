"""
AWS S3 service for file storage and management
"""

import boto3
import uuid
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for managing file uploads and storage in AWS S3"""
    
    def __init__(self):
        """Initialize S3 client"""
        try:
            # Check if AWS credentials are provided
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                logger.warning("AWS credentials not provided - S3 service will be disabled")
                self.s3_client = None
                self.bucket_name = settings.AWS_S3_BUCKET
                return
                
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.AWS_S3_BUCKET
            self._ensure_bucket_exists()
        except NoCredentialsError:
            logger.warning("AWS credentials not found - S3 service will be disabled")
            self.s3_client = None
            self.bucket_name = settings.AWS_S3_BUCKET
        except Exception as e:
            logger.warning(f"Failed to initialize S3 client: {str(e)} - S3 service will be disabled")
            self.s3_client = None
            self.bucket_name = settings.AWS_S3_BUCKET
    
    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists, create if it doesn't"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket {self.bucket_name} exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION}
                    )
                    logger.info(f"Created S3 bucket {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create S3 bucket: {str(create_error)}")
                    raise HTTPException(status_code=500, detail="Failed to create S3 bucket")
            else:
                logger.error(f"Error checking S3 bucket: {str(e)}")
                raise HTTPException(status_code=500, detail="S3 bucket access error")
    
    def generate_upload_key(self, user_id: str, submission_id: str, filename: str) -> str:
        """Generate a unique S3 key for file upload"""
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        unique_id = str(uuid.uuid4())
        return f"submissions/{user_id}/{submission_id}/{unique_id}.{file_extension}"
    
    def generate_presigned_upload_url(
        self, 
        key: str, 
        content_type: str, 
        expires_in: int = 3600
    ) -> Dict[str, Any]:
        """Generate a presigned URL for file upload"""
        try:
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 1, settings.MAX_FILE_SIZE]
                ],
                ExpiresIn=expires_in
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned upload URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate upload URL")
    
    def generate_presigned_download_url(
        self, 
        key: str, 
        expires_in: int = 3600
    ) -> str:
        """Generate a presigned URL for file download"""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned download URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate download URL")
    
    def delete_file(self, key: str) -> bool:
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted file from S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            return False
    
    def get_file_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from S3"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response['ContentType'],
                'etag': response['ETag']
            }
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            logger.error(f"Failed to get file metadata: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get file metadata")
    
    def copy_file(self, source_key: str, dest_key: str) -> bool:
        """Copy a file within S3"""
        try:
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=dest_key
            )
            logger.info(f"Copied file from {source_key} to {dest_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to copy file: {str(e)}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """List files in the bucket with optional prefix"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"Failed to list files: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to list files")


# Global S3 service instance
s3_service = S3Service()
