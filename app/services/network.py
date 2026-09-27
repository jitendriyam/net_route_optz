from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictError, NotFoundError
from app.graph.builder import GraphBuilder
from app.graph.shortest_path import Dijkstra
from app.repositories.edges import EdgeRepository
from app.repositories.nodes import NodeRepository
from app.repositories.route_history import RouteHistoryRepository


class NodeService:
    def __init__(self, session):
        self.session = session
        self.nodes = NodeRepository(session)

    def require(self, name: str):
        node = self.nodes.get_by_name(name)
        if node is None:
            raise NotFoundError(f"Node '{name}' not found")
        return node

    def create(self, name: str):
        if self.nodes.get_by_name(name) is not None:
            raise ConflictError(f"Node '{name}' already exists")
        try:
            node = self.nodes.create(name)
            self.session.commit()
            return node
        except IntegrityError:
            self.session.rollback()
            if self.nodes.get_by_name(name) is not None:
                raise ConflictError(f"Node '{name}' already exists") from None
            raise

    def list(self) -> list:
        return self.nodes.list_all()

    def delete(self, node_id: int) -> None:
        node = self.nodes.get_by_id(node_id)
        if node is None:
            raise NotFoundError(f"Node {node_id} not found")
        self.nodes.delete(node)
        self.session.commit()


class EdgeService:
    def __init__(self, session):
        self.session = session
        self.nodes = NodeService(session)
        self.edges = EdgeRepository(session)

    def create(self, source: str, destination: str, latency: float):
        source_id = self.nodes.require(source).id
        destination_id = self.nodes.require(destination).id
        if self.edges.fetch_between(source_id, destination_id) is not None:
            raise ConflictError("Directed edge already exists")
        try:
            edge = self.edges.create(source_id, destination_id, latency)
            self.session.commit()
            return edge
        except IntegrityError:
            self.session.rollback()
            if self.edges.fetch_between(source_id, destination_id) is not None:
                raise ConflictError("Directed edge already exists") from None
            # A node may have been deleted after the initial validation.
            self.nodes.require(source)
            self.nodes.require(destination)
            raise

    def list(self) -> list:
        return self.edges.list_with_node_names()

    def delete(self, edge_id: int) -> None:
        edge = self.edges.get_by_id(edge_id)
        if edge is None:
            raise NotFoundError(f"Edge {edge_id} not found")
        self.edges.delete(edge)
        self.session.commit()


class RouteService:
    def __init__(self, session, algorithm=None):
        self.session = session
        self.nodes = NodeService(session)
        self.edges = EdgeRepository(session)
        self.history = RouteHistoryRepository(session)
        self.builder = GraphBuilder()
        # Engines share the ShortestPathAlgorithm.find_path contract.
        self.algorithm = algorithm if algorithm is not None else Dijkstra()

    def shortest(self, source: str, destination: str) -> dict:
        self.nodes.require(source)
        self.nodes.require(destination)
        graph = self.builder.build(
            (node.name for node in self.nodes.list()),
            (
                (src, dst, latency)
                for _, src, dst, latency in self.edges.list_with_node_names()
            ),
        )
        result = self.algorithm.find_path(graph, source, destination)
        if result is None:
            raise NotFoundError(f"No route from '{source}' to '{destination}'")
        self.history.create(source, destination, result["total_latency"], result["path"])
        self.session.commit()
        return result

    def list_history(self, filters) -> list:
        values = filters.model_dump()
        return self.history.filter(
            source_name=values["source"],
            destination_name=values["destination"],
            created_from=values["date_from"],
            created_to=values["date_to"],
            limit=values["limit"],
        )
