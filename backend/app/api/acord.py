"""
ACORD form API endpoints
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/convert")
async def convert_to_acord():
    """Convert extracted data to ACORD schema"""
    # TODO: Implement ACORD conversion logic
    return {"message": "ACORD conversion endpoint - to be implemented"}


@router.get("/schema")
async def get_acord_schema():
    """Get ACORD 125 schema definition"""
    # TODO: Implement schema retrieval
    return {"message": "ACORD schema endpoint - to be implemented"}
