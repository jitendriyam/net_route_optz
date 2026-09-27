import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictError, NotFoundError
from app.schemas.network import HistoryFilters
from app.services.network import EdgeService, NodeService, RouteService


def create_nodes(session, *names: str) -> None:
    service = NodeService(session)
    for name in names:
        service.create(name)


def create_edge(session, source: str, destination: str, latency: float):
    return EdgeService(session).create(source, destination, latency)


def test_node_creation(session) -> None:
    node = NodeService(session).create("ServerA")

    assert node.id is not None
    assert node.name == "ServerA"


def test_duplicate_node(session) -> None:
    service = NodeService(session)
    service.create("ServerA")

    with pytest.raises(ConflictError, match="already exists"):
        service.create("ServerA")


def test_edge_creation(session) -> None:
    create_nodes(session, "ServerA", "ServerB")

    edge = create_edge(session, "ServerA", "ServerB", 12.5)

    assert edge.id is not None
    assert edge.latency == 12.5


def test_duplicate_edge(session) -> None:
    create_nodes(session, "ServerA", "ServerB")
    create_edge(session, "ServerA", "ServerB", 12.5)

    with pytest.raises(ConflictError, match="already exists"):
        create_edge(session, "ServerA", "ServerB", 20)


def test_invalid_latency(session) -> None:
    create_nodes(session, "ServerA", "ServerB")

    with pytest.raises(IntegrityError):
        create_edge(session, "ServerA", "ServerB", 0)


def test_missing_nodes(session) -> None:
    with pytest.raises(NotFoundError, match="ServerA"):
        create_edge(session, "ServerA", "ServerB", 12.5)


def test_short_direct_route(session) -> None:
    create_nodes(session, "ServerA", "ServerB")
    create_edge(session, "ServerA", "ServerB", 12.5)

    result = RouteService(session).shortest("ServerA", "ServerB")

    assert result == {"path": ["ServerA", "ServerB"], "total_latency": 12.5}


def test_shortest_multi_hop_route(session) -> None:
    create_nodes(session, "ServerA", "ServerB", "ServerC")
    create_edge(session, "ServerA", "ServerB", 5)
    create_edge(session, "ServerB", "ServerC", 7)

    result = RouteService(session).shortest("ServerA", "ServerC")

    assert result == {"path": ["ServerA", "ServerB", "ServerC"], "total_latency": 12}


def test_competing_routes(session) -> None:
    create_nodes(session, "ServerA", "ServerB", "ServerC", "ServerD")
    create_edge(session, "ServerA", "ServerB", 4)
    create_edge(session, "ServerB", "ServerD", 8)
    create_edge(session, "ServerA", "ServerC", 2)
    create_edge(session, "ServerC", "ServerD", 3)

    result = RouteService(session).shortest("ServerA", "ServerD")

    assert result == {"path": ["ServerA", "ServerC", "ServerD"], "total_latency": 5}


def test_no_available_route(session) -> None:
    create_nodes(session, "ServerA", "ServerB")

    with pytest.raises(NotFoundError, match="No route"):
        RouteService(session).shortest("ServerA", "ServerB")


def test_route_history_creation(session) -> None:
    create_nodes(session, "ServerA", "ServerB")
    create_edge(session, "ServerA", "ServerB", 12.5)

    RouteService(session).shortest("ServerA", "ServerB")

    history = RouteService(session).list_history(HistoryFilters())
    assert len(history) == 1
    assert history[0].path == ["ServerA", "ServerB"]
    assert history[0].total_latency == 12.5


def test_history_filters(session) -> None:
    create_nodes(session, "ServerA", "ServerB", "ServerC")
    create_edge(session, "ServerA", "ServerB", 5)
    create_edge(session, "ServerB", "ServerC", 7)
    route_service = RouteService(session)
    route_service.shortest("ServerA", "ServerB")
    route_service.shortest("ServerA", "ServerC")

    history = route_service.list_history(
        HistoryFilters(source="ServerA", destination="ServerC", limit=1)
    )

    assert len(history) == 1
    assert history[0].source_name == "ServerA"
    assert history[0].destination_name == "ServerC"


def test_node_deletion_cascades_to_edges(session) -> None:
    create_nodes(session, "ServerA", "ServerB", "ServerC")
    create_edge(session, "ServerA", "ServerB", 5)
    create_edge(session, "ServerC", "ServerA", 7)
    node_service = NodeService(session)
    node_service.delete(node_service.nodes.get_by_name("ServerA").id)

    assert EdgeService(session).list() == []
