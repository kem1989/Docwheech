"""
File validation service for uploads
"""

import os
from typing import Dict, List, Tuple, Optional
from fastapi import HTTPException
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Try to import magic, fallback if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    logger.warning("python-magic not available, file validation will be limited")
    MAGIC_AVAILABLE = False


class FileValidationService:
    """Service for validating uploaded files"""
    
    def __init__(self):
        """Initialize file validation service"""
        self.allowed_types = settings.ALLOWED_FILE_TYPES.split(",")
        self.max_size = settings.MAX_FILE_SIZE
        
        # MIME type mapping for validation
        self.mime_type_map = {
            'pdf': ['application/pdf'],
            'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            'jpg': ['image/jpeg'],
            'jpeg': ['image/jpeg'],
            'png': ['image/png'],
            'doc': ['application/msword'],
            'xls': ['application/vnd.ms-excel']
        }
    
    def validate_file(
        self, 
        filename: str, 
        content: bytes, 
        mime_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Validate uploaded file
        
        Returns:
            Tuple of (is_valid, error_message, detected_file_type)
        """
        try:
            # Check file size
            if len(content) > self.max_size:
                return False, f"File size exceeds maximum allowed size of {self.max_size / (1024*1024):.1f}MB", ""
            
            # Check if file is empty
            if len(content) == 0:
                return False, "File is empty", ""
            
            # Get file extension
            file_extension = self._get_file_extension(filename)
            if not file_extension:
                return False, "File must have a valid extension", ""
            
            # Check if file type is allowed
            if file_extension not in self.allowed_types:
                return False, f"File type '{file_extension}' is not allowed. Allowed types: {', '.join(self.allowed_types)}", ""
            
            # Detect actual file type using python-magic
            if MAGIC_AVAILABLE:
                detected_mime = magic.from_buffer(content, mime=True)
            else:
                # Fallback: use file extension for MIME type
                detected_mime = self._get_mime_from_extension(file_extension)
            
            # Validate MIME type matches extension
            expected_mimes = self.mime_type_map.get(file_extension, [])
            if expected_mimes and detected_mime not in expected_mimes:
                # If provided MIME type matches expected, use that instead
                if mime_type and mime_type in expected_mimes:
                    detected_mime = mime_type
                else:
                    return False, f"File content doesn't match extension. Detected: {detected_mime}, Expected: {file_extension}", ""
            
            # Additional file-specific validations
            validation_result = self._validate_file_content(file_extension, content)
            if not validation_result[0]:
                return validation_result
            
            return True, None, file_extension
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False, f"File validation failed: {str(e)}", ""
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        if '.' not in filename:
            return ""
        return filename.split('.')[-1].lower()
    
    def _validate_file_content(self, file_type: str, content: bytes) -> Tuple[bool, Optional[str], str]:
        """Validate file content based on type"""
        try:
            if file_type == 'pdf':
                return self._validate_pdf(content)
            elif file_type in ['docx', 'doc']:
                return self._validate_document(content)
            elif file_type in ['xlsx', 'xls']:
                return self._validate_spreadsheet(content)
            elif file_type in ['jpg', 'jpeg', 'png']:
                return self._validate_image(content)
            else:
                return True, None, file_type
        except Exception as e:
            logger.error(f"Content validation error for {file_type}: {str(e)}")
            return False, f"File content validation failed: {str(e)}", file_type
    
    def _validate_pdf(self, content: bytes) -> Tuple[bool, Optional[str], str]:
        """Validate PDF file"""
        try:
            # Check PDF header
            if not content.startswith(b'%PDF-'):
                return False, "File is not a valid PDF", "pdf"
            
            # Check for PDF trailer
            if b'%%EOF' not in content[-1024:]:
                return False, "PDF file appears to be corrupted", "pdf"
            
            return True, None, "pdf"
        except Exception as e:
            return False, f"PDF validation failed: {str(e)}", "pdf"
    
    def _validate_document(self, content: bytes) -> Tuple[bool, Optional[str], str]:
        """Validate Word document"""
        try:
            # Check for ZIP-based format (docx)
            if content.startswith(b'PK'):
                return True, None, "docx"
            
            # Check for OLE format (doc)
            if content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
                return True, None, "doc"
            
            return False, "File is not a valid Word document", "docx"
        except Exception as e:
            return False, f"Document validation failed: {str(e)}", "docx"
    
    def _validate_spreadsheet(self, content: bytes) -> Tuple[bool, Optional[str], str]:
        """Validate Excel spreadsheet"""
        try:
            # Check for ZIP-based format (xlsx)
            if content.startswith(b'PK'):
                return True, None, "xlsx"
            
            # Check for OLE format (xls)
            if content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
                return True, None, "xls"
            
            return False, "File is not a valid Excel spreadsheet", "xlsx"
        except Exception as e:
            return False, f"Spreadsheet validation failed: {str(e)}", "xlsx"
    
    def _validate_image(self, content: bytes) -> Tuple[bool, Optional[str], str]:
        """Validate image file"""
        try:
            # Check for common image headers
            if content.startswith(b'\xff\xd8\xff'):  # JPEG
                return True, None, "jpg"
            elif content.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                return True, None, "png"
            else:
                return False, "File is not a valid image", "jpg"
        except Exception as e:
            return False, f"Image validation failed: {str(e)}", "jpg"
    
    def _get_mime_from_extension(self, extension: str) -> str:
        """Get MIME type from file extension as fallback"""
        mime_map = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'doc': 'application/msword',
            'xls': 'application/vnd.ms-excel'
        }
        return mime_map.get(extension, 'application/octet-stream')

    def get_file_info(self, filename: str, content: bytes) -> Dict[str, any]:
        """Get comprehensive file information"""
        is_valid, error, file_type = self.validate_file(filename, content)
        
        mime_type = None
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_buffer(content, mime=True)
            except:
                mime_type = self._get_mime_from_extension(file_type)
        else:
            mime_type = self._get_mime_from_extension(file_type)
        
        return {
            'filename': filename,
            'file_type': file_type,
            'size': len(content),
            'is_valid': is_valid,
            'error': error,
            'mime_type': mime_type
        }


# Global file validation service instance
file_validation_service = FileValidationService()



