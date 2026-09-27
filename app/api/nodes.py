from fastapi import APIRouter, Depends, Response

from app.db.session import get_session
from app.schemas.network import NodeCreate, NodeResponse
from app.services.network import NodeService

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.post("", response_model=NodeResponse, status_code=201)
def create_node(body: NodeCreate, session=Depends(get_session)):
    """Create a uniquely named network node."""
    return NodeResponse.model_validate(NodeService(session).create(body.name))


@router.get("", response_model=list[NodeResponse])
def list_nodes(session=Depends(get_session)):
    """Return all network nodes."""
    return [NodeResponse.model_validate(node) for node in NodeService(session).list()]


@router.delete("/{node_id}", status_code=204)
def delete_node(node_id: int, session=Depends(get_session)):
    """Delete a node and its incoming and outgoing edges."""
    NodeService(session).delete(node_id)
    return Response(status_code=204)
