from fastapi import APIRouter
from typing import Dict

# Note: This translation router is deprecated as we now use direct multilingual fields (_en, _es)
# instead of a separate translations table. All endpoints have been disabled.

router = APIRouter(prefix="/translations", tags=["translations"])


@router.get("/status")
async def translation_status():
    """Status endpoint indicating that translation endpoints are deprecated."""
    return {
        "status": "deprecated", 
        "message": "Translation endpoints are deprecated. Using direct multilingual fields instead.",
        "migration_info": "Content now uses _en and _es suffixes for multilingual support"
    }