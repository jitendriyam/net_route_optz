from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictError
from app.repositories.edges import EdgeRepository
from app.repositories.nodes import NodeRepository


class TestDataService:
    """Create and remove the deterministic sample network used for manual testing."""

    nodes = ("TestA", "TestB", "TestC", "TestD")
    edges = (
        ("TestA", "TestB", 5.0),
        ("TestB", "TestD", 8.0),
        ("TestA", "TestC", 2.0),
        ("TestC", "TestD", 3.0),
    )

    def __init__(self, session) -> None:
        self.session = session
        self.node_repository = NodeRepository(session)
        self.edge_repository = EdgeRepository(session)

    def create(self) -> dict:
        if any(self.node_repository.get_by_name(name) for name in self.nodes):
            raise ConflictError("Test data already exists")

        try:
            created_nodes = {
                name: self.node_repository.create(name) for name in self.nodes
            }
            for source, destination, latency in self.edges:
                self.edge_repository.create(
                    created_nodes[source].id,
                    created_nodes[destination].id,
                    latency,
                )
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise ConflictError("Test data already exists") from None

        return {
            "nodes": list(self.nodes),
            "edges": [
                {"source": source, "destination": destination, "latency": latency}
                for source, destination, latency in self.edges
            ],
        }

    def delete(self) -> None:
        for name in self.nodes:
            node = self.node_repository.get_by_name(name)
            if node is not None:
                self.node_repository.delete(node)
        self.session.commit()
