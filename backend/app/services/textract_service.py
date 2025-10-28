"""
AWS Textract service for document text extraction
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class TextractService:
    """Service for AWS Textract document processing"""
    
    def __init__(self):
        """Initialize Textract client"""
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            logger.warning("AWS credentials not provided - Textract service will be disabled")
            self.textract_client = None
            return
            
        try:
            self.textract_client = boto3.client(
                'textract',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            logger.info("AWS Textract client initialized successfully")
        except NoCredentialsError:
            logger.warning("AWS credentials not found - Textract service will be disabled")
            self.textract_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Textract client: {str(e)}")
            self.textract_client = None
    
    def extract_text_from_s3(
        self, 
        bucket: str, 
        key: str, 
        document_type: str = "pdf"
    ) -> Dict[str, Any]:
        """
        Extract text from document stored in S3 using Textract
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            document_type: Type of document (pdf, image, etc.)
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        if not self.textract_client:
            raise HTTPException(status_code=503, detail="Textract service not available")
        
        try:
            # Determine the appropriate Textract API based on document type
            if document_type.lower() in ['pdf']:
                # Use asynchronous processing for PDFs
                return self._process_pdf_document(bucket, key)
            else:
                # Use synchronous processing for images
                return self._process_image_document(bucket, key)
                
        except ClientError as e:
            logger.error(f"Textract processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Textract processing: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Document processing error: {str(e)}")
    
    def _process_pdf_document(self, bucket: str, key: str) -> Dict[str, Any]:
        """Process PDF document using asynchronous Textract"""
        try:
            # Start asynchronous job
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            
            job_id = response['JobId']
            logger.info(f"Started Textract job {job_id} for PDF {key}")
            
            # Wait for job completion
            job_result = self._wait_for_job_completion(job_id)
            
            # Extract text from results
            extracted_text = self._extract_text_from_blocks(job_result.get('Blocks', []))
            
            return {
                'text': extracted_text,
                'job_id': job_id,
                'status': 'completed',
                'page_count': self._count_pages(job_result.get('Blocks', [])),
                'confidence_scores': self._calculate_confidence_scores(job_result.get('Blocks', []))
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
    
    def _process_image_document(self, bucket: str, key: str) -> Dict[str, Any]:
        """Process image document using synchronous Textract"""
        try:
            response = self.textract_client.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            
            # Extract text from results
            extracted_text = self._extract_text_from_blocks(response.get('Blocks', []))
            
            return {
                'text': extracted_text,
                'status': 'completed',
                'page_count': 1,
                'confidence_scores': self._calculate_confidence_scores(response.get('Blocks', []))
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")
    
    def _wait_for_job_completion(self, job_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """Wait for Textract job completion"""
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = self.textract_client.get_document_text_detection(JobId=job_id)
            status = response['JobStatus']
            
            if status == 'SUCCEEDED':
                return response
            elif status == 'FAILED':
                error_message = response.get('StatusMessage', 'Unknown error')
                raise HTTPException(status_code=500, detail=f"Textract job failed: {error_message}")
            
            # Wait before checking again
            time.sleep(5)
        
        raise HTTPException(status_code=408, detail="Textract job timeout")
    
    def _extract_text_from_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        """Extract text from Textract blocks"""
        text_lines = []
        
        # Sort blocks by page and then by position
        sorted_blocks = sorted(blocks, key=lambda x: (x.get('Page', 0), x.get('Top', 0)))
        
        for block in sorted_blocks:
            if block['BlockType'] == 'LINE':
                text_lines.append(block['Text'])
        
        return '\n'.join(text_lines)
    
    def _count_pages(self, blocks: List[Dict[str, Any]]) -> int:
        """Count the number of pages in the document"""
        pages = set()
        for block in blocks:
            if 'Page' in block:
                pages.add(block['Page'])
        return len(pages)
    
    def _calculate_confidence_scores(self, blocks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average confidence scores for the document"""
        line_confidences = []
        word_confidences = []
        
        for block in blocks:
            if block['BlockType'] == 'LINE' and 'Confidence' in block:
                line_confidences.append(block['Confidence'])
            elif block['BlockType'] == 'WORD' and 'Confidence' in block:
                word_confidences.append(block['Confidence'])
        
        return {
            'average_line_confidence': sum(line_confidences) / len(line_confidences) if line_confidences else 0.0,
            'average_word_confidence': sum(word_confidences) / len(word_confidences) if word_confidences else 0.0,
            'total_lines': len(line_confidences),
            'total_words': len(word_confidences)
        }
    
    def extract_tables_from_s3(
        self, 
        bucket: str, 
        key: str
    ) -> List[Dict[str, Any]]:
        """
        Extract tables from document using Textract
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            List of extracted tables with structured data
        """
        if not self.textract_client:
            raise HTTPException(status_code=503, detail="Textract service not available")
        
        try:
            response = self.textract_client.analyze_document(
                Document={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                },
                FeatureTypes=['TABLES']
            )
            
            tables = self._extract_tables_from_blocks(response.get('Blocks', []))
            return tables
            
        except Exception as e:
            logger.error(f"Table extraction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Table extraction failed: {str(e)}")
    
    def _extract_tables_from_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract structured tables from Textract blocks"""
        tables = []
        table_blocks = [block for block in blocks if block['BlockType'] == 'TABLE']
        
        for table_block in table_blocks:
            table_data = self._build_table_structure(table_block, blocks)
            tables.append(table_data)
        
        return tables
    
    def _build_table_structure(
        self, 
        table_block: Dict[str, Any], 
        all_blocks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build structured table data from table block"""
        # This is a simplified implementation
        # In production, you'd want more sophisticated table reconstruction
        table_data = {
            'table_id': table_block['Id'],
            'confidence': table_block.get('Confidence', 0.0),
            'rows': [],
            'raw_data': []
        }
        
        # Get all cells in this table
        cell_blocks = [block for block in all_blocks 
                      if block.get('BlockType') == 'CELL' and 
                      table_block['Id'] in block.get('Relationships', [{}])[0].get('Ids', [])]
        
        # Group cells by row
        rows = {}
        for cell in cell_blocks:
            row_index = cell.get('RowIndex', 0)
            col_index = cell.get('ColumnIndex', 0)
            
            if row_index not in rows:
                rows[row_index] = {}
            
            # Get text from child blocks
            cell_text = self._get_cell_text(cell, all_blocks)
            rows[row_index][col_index] = cell_text
        
        # Convert to list format
        for row_index in sorted(rows.keys()):
            row_data = []
            for col_index in sorted(rows[row_index].keys()):
                row_data.append(rows[row_index][col_index])
            table_data['rows'].append(row_data)
        
        return table_data
    
    def _get_cell_text(self, cell_block: Dict[str, Any], all_blocks: List[Dict[str, Any]]) -> str:
        """Extract text from a table cell"""
        text_parts = []
        
        # Get child block IDs
        child_ids = []
        for relationship in cell_block.get('Relationships', []):
            if relationship['Type'] == 'CHILD':
                child_ids.extend(relationship['Ids'])
        
        # Get text from child blocks
        for block in all_blocks:
            if block['Id'] in child_ids and block['BlockType'] == 'WORD':
                text_parts.append(block['Text'])
        
        return ' '.join(text_parts)


# Global Textract service instance
textract_service = TextractService()
