from fastapi import APIRouter, Depends, HTTPException, Query
from app.dependencies import get_search_service
from app.service.search_service import SearchService
from app.models.Responses.service_responses import ServiceBaseResponse
from app.models.Responses.service_responses import ServiceCategoryResponse
from typing import List, Optional

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/services", response_model=List[ServiceBaseResponse])
async def search_services(
    q: Optional[str] = Query(None, description="Search query for service title/description"),
    category: Optional[str] = Query(None, description="Category name (fuzzy matched)"),
    location: Optional[str] = Query(None, description="Location (fuzzy matched)"),
    max_distance_km: Optional[int] = Query(None, description="Maximum distance in km"),
    min_trust_score: Optional[int] = Query(None, description="Minimum trust score"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    limit: int = Query(50, description="Number of results"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Advanced fuzzy search for services
    """
    try:
        services = search_service.fuzzy_search_services(
            query=q,
            category_name=category,
            location=location,
            max_distance_km=max_distance_km,
            min_trust_score=min_trust_score,
            max_price=max_price,
            limit=limit
        )
        
        return [ServiceBaseResponse.model_validate(service) for service in services]
        
    except Exception as e:
        raise HTTPException(500, detail="Search service temporarily unavailable")

@router.get("/categories", response_model=List[ServiceCategoryResponse])
async def search_categories(
    q: str = Query(..., description="Search query for category names"),
    limit: int = Query(20, description="Number of results"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Fuzzy search for categories
    """
    try:
        categories = search_service.search_categories_fuzzy(q, limit)
        return [ServiceCategoryResponse.model_validate(cat) for cat in categories]
        
    except Exception as e:
        raise HTTPException(500, detail="Category search temporarily unavailable")

@router.get("/autocomplete/services")
async def autocomplete_services(
    q: str = Query(..., description="Partial service title for autocomplete"),
    limit: int = Query(10, description="Number of suggestions"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Autocomplete service titles
    """
    try:
        suggestions = search_service.autocomplete_services(q, limit)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(500, detail="Autocomplete service unavailable")

@router.get("/autocomplete/categories")
async def autocomplete_categories(
    q: str = Query(..., description="Partial category name for autocomplete"),
    limit: int = Query(10, description="Number of suggestions"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Autocomplete category names
    """
    try:
        suggestions = search_service.autocomplete_categories(q, limit)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(500, detail="Autocomplete service unavailable")