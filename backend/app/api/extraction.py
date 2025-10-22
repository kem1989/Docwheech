"""
AI extraction API endpoints
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/extract")
async def extract_data():
    """Extract data from uploaded files using AI"""
    # TODO: Implement AI extraction logic
    return {"message": "AI extraction endpoint - to be implemented"}


@router.get("/extraction/{extraction_id}")
async def get_extraction_result(extraction_id: str):
    """Get extraction results"""
    # TODO: Implement extraction result retrieval
    return {"message": f"Extraction {extraction_id} - to be implemented"}
