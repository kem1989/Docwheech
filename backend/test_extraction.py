"""
Test utilities for AI extraction testing
"""

import json
import requests
import time
from typing import Dict, Any, List
import uuid


class AIExtractionTester:
    """Test utility for AI extraction functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize tester with API base URL"""
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
    
    def authenticate(self, email: str = "test@example.com", password: str = "testpassword"):
        """Authenticate with the API (not needed for test endpoints)"""
        # Test endpoints don't require authentication
        print("✅ Using test endpoints (no authentication required)")
        return True
    
    def upload_test_document(self, file_path: str, filename: str) -> str:
        """Upload a test document and return the S3 key"""
        # This is a mock implementation
        # In real testing, you'd upload to S3 and get the actual key
        mock_key = f"test-documents/{uuid.uuid4()}/{filename}"
        print(f"✅ Mock document uploaded: {mock_key}")
        return mock_key
    
    def start_extraction(self, submission_id: str, document_keys: List[str], confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Start AI extraction process"""
        url = f"{self.base_url}/api/extraction/test-extract"
        
        payload = {
            "submission_id": submission_id,
            "document_keys": document_keys,
            "confidence_threshold": confidence_threshold
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"✅ Extraction started: {result}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to start extraction: {e}")
            return {}
    
    def check_extraction_status(self, extraction_id: str) -> Dict[str, Any]:
        """Check extraction status"""
        url = f"{self.base_url}/api/extraction/test-extraction/{extraction_id}/status"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            result = response.json()
            print(f"📊 Extraction status: {result}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get status: {e}")
            return {}
    
    def get_extraction_results(self, extraction_id: str) -> Dict[str, Any]:
        """Get extraction results"""
        url = f"{self.base_url}/api/extraction/test-extraction/{extraction_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            result = response.json()
            print(f"✅ Extraction results retrieved")
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get results: {e}")
            return {}
    
    def wait_for_completion(self, extraction_id: str, max_wait_time: int = 300) -> bool:
        """Wait for extraction to complete"""
        print(f"⏳ Waiting for extraction {extraction_id} to complete...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            status = self.check_extraction_status(extraction_id)
            
            if status.get("extraction_status") == "completed":
                print("✅ Extraction completed!")
                return True
            elif status.get("extraction_status") == "failed":
                print("❌ Extraction failed!")
                return False
            
            progress = status.get("extraction_progress", 0)
            print(f"📈 Progress: {progress}%")
            
            time.sleep(5)  # Wait 5 seconds before checking again
        
        print("⏰ Extraction timeout")
        return False
    
    def run_full_test(self, document_paths: List[str]) -> Dict[str, Any]:
        """Run a complete extraction test"""
        print("🚀 Starting AI Extraction Test")
        print("=" * 50)
        
        # Generate test submission ID
        submission_id = str(uuid.uuid4())
        print(f"📝 Submission ID: {submission_id}")
        
        # Upload documents (mock)
        document_keys = []
        for doc_path in document_paths:
            filename = doc_path.split("/")[-1]
            key = self.upload_test_document(doc_path, filename)
            document_keys.append(key)
        
        # Start extraction
        extraction_result = self.start_extraction(submission_id, document_keys)
        
        if not extraction_result:
            return {"error": "Failed to start extraction"}
        
        # Wait for completion
        completed = self.wait_for_completion(submission_id)
        
        if not completed:
            return {"error": "Extraction did not complete"}
        
        # Get results
        results = self.get_extraction_results(submission_id)
        
        print("=" * 50)
        print("🎉 Test completed!")
        
        return results


def create_sample_insurance_document():
    """Create a sample insurance document for testing"""
    sample_content = """
    COMMERCIAL INSURANCE APPLICATION
    
    Company Information:
    Company Name: Acme Manufacturing Corp.
    DBA: Acme Manufacturing
    Business Address: 123 Industrial Way, Dallas, TX 75201
    Phone: (214) 555-1234
    Email: info@acmemanufacturing.com
    Website: www.acmemanufacturing.com
    Federal Tax ID: 12-3456789
    State of Incorporation: Texas
    Years in Business: 15
    Number of Employees: 45
    Annual Revenue: $2,500,000
    
    Business Description:
    Acme Manufacturing Corp. is a leading manufacturer of industrial equipment and machinery. 
    We specialize in custom manufacturing solutions for the automotive and aerospace industries.
    Our facility operates 24/7 with state-of-the-art equipment and employs skilled technicians.
    
    Coverage Information:
    Coverage Type: General Liability
    Policy Effective Date: January 1, 2024
    Policy Expiration Date: January 1, 2025
    Annual Premium: $15,000
    Policy Number: GL-2024-001
    Carrier: ABC Insurance Company
    Policy Limit: $2,000,000
    Deductible: $5,000
    
    Broker Information:
    Broker Name: John Smith
    Broker Email: john.smith@insuranceagency.com
    Broker Phone: (555) 123-4567
    Agency Name: Smith Insurance Agency
    Agency Address: 456 Business Blvd, Dallas, TX 75202
    License Number: TX-123456
    
    Risk Information:
    Our manufacturing operations include:
    - Metal fabrication and welding
    - Precision machining
    - Assembly operations
    - Quality control testing
    
    Safety Programs:
    - OSHA compliance training
    - Safety committee meetings
    - Regular equipment maintenance
    - Employee safety training
    
    Previous Claims:
    - 2022: Minor property damage claim ($2,500)
    - 2021: Workers compensation claim ($8,000)
    - No other claims in the past 5 years
    """
    
    return sample_content


if __name__ == "__main__":
    # Example usage
    tester = AIExtractionTester()
    
    # Create sample document
    sample_doc = create_sample_insurance_document()
    print("Sample document created:")
    print(sample_doc[:200] + "...")
    
    # Run test
    results = tester.run_full_test(["sample_insurance_app.pdf"])
    print("\nTest Results:")
    print(json.dumps(results, indent=2))
