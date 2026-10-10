from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.search_service import SearchService

router = APIRouter()
search_service = SearchService()


@router.get("/")
async def search(
    q: str = Query(..., min_length=1, description="Search term"),
    type: str = Query("all", description="Filter by type: all, festivals, users, shortfilms"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = search_service.search_all(db, q, type)
    total = len(results["festivals"]) + len(results["users"]) + len(results["shortfilms"])
    return {"query": q, "total": total, "results": results}
