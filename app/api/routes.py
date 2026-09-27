from fastapi import APIRouter, Depends, Query

from app.db.session import get_session
from app.schemas.network import (
    HistoryFilters,
    HistoryResponse,
    RouteRequest,
    RouteResponse,
)
from app.services.network import RouteService

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/shortest", response_model=RouteResponse)
def shortest_route(body: RouteRequest, session=Depends(get_session)):
    """Calculate and store the minimum-latency route between two nodes."""
    return RouteService(session).shortest(body.source, body.destination)


@router.get("/history", response_model=list[HistoryResponse])
def route_history(filters: HistoryFilters = Query(), session=Depends(get_session)):
    """Return successful route-history snapshots matching the filters."""
    return [
        HistoryResponse.model_validate(history)
        for history in RouteService(session).list_history(filters)
    ]
