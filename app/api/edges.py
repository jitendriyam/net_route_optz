from fastapi import APIRouter, Depends, Response

from app.db.session import get_session
from app.schemas.network import EdgeCreate, EdgeResponse
from app.services.network import EdgeService

router = APIRouter(prefix="/edges", tags=["edges"])


@router.post("", response_model=EdgeResponse, status_code=201)
def create_edge(body: EdgeCreate, session=Depends(get_session)):
    """Create a directed edge between two existing nodes."""
    edge = EdgeService(session).create(body.source, body.destination, body.latency)
    return EdgeResponse(id=edge.id, **body.model_dump())


@router.get("", response_model=list[EdgeResponse])
def list_edges(session=Depends(get_session)):
    """Return all directed network edges."""
    return [
        EdgeResponse(id=edge_id, source=source, destination=destination, latency=latency)
        for edge_id, source, destination, latency in EdgeService(session).list()
    ]


@router.delete("/{edge_id}", status_code=204)
def delete_edge(edge_id: int, session=Depends(get_session)):
    """Delete a directed edge by identifier."""
    EdgeService(session).delete(edge_id)
    return Response(status_code=204)
