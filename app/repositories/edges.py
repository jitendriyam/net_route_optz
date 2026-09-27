from sqlalchemy import delete, select
from sqlalchemy.orm import Session, aliased

from app.models.network import Edge, Node


class EdgeRepository:
    """Database access for directed edges only."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, edge_id: int) -> Edge | None:
        return self.session.get(Edge, edge_id)

    def fetch_all(self) -> list[Edge]:
        statement = select(Edge).order_by(Edge.source_id, Edge.destination_id)
        return list(self.session.scalars(statement))

    def list_with_node_names(self) -> list[tuple[int, str, str, float]]:
        source = aliased(Node)
        destination = aliased(Node)
        statement = (
            select(Edge.id, source.name, destination.name, Edge.latency)
            .join(source, source.id == Edge.source_id)
            .join(destination, destination.id == Edge.destination_id)
            .order_by(Edge.id)
        )
        return list(self.session.execute(statement))

    def fetch_from_node(self, source_id: int) -> list[Edge]:
        statement = select(Edge).where(Edge.source_id == source_id).order_by(Edge.destination_id)
        return list(self.session.scalars(statement))

    def fetch_between(self, source_id: int, destination_id: int) -> Edge | None:
        statement = select(Edge).where(
            Edge.source_id == source_id,
            Edge.destination_id == destination_id,
        )
        return self.session.scalar(statement)

    def create(self, source_id: int, destination_id: int, latency: float) -> Edge:
        edge = Edge(
            source_id=source_id,
            destination_id=destination_id,
            latency=latency,
        )
        self.session.add(edge)
        self.session.flush()
        return edge

    def delete(self, edge: Edge) -> None:
        self.session.delete(edge)
        self.session.flush()

    def delete_by_id(self, edge_id: int) -> bool:
        result = self.session.execute(delete(Edge).where(Edge.id == edge_id))
        self.session.flush()
        return result.rowcount > 0
