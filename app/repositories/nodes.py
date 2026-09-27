from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.network import Node


class NodeRepository:
    """Database access for nodes only."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_name(self, name: str) -> Node | None:
        return self.session.scalar(select(Node).where(Node.name == name))

    def get_by_id(self, node_id: int) -> Node | None:
        return self.session.get(Node, node_id)

    def list_all(self) -> list[Node]:
        return list(self.session.scalars(select(Node).order_by(Node.name)))

    def create(self, name: str) -> Node:
        node = Node(name=name)
        self.session.add(node)
        self.session.flush()
        return node

    def delete(self, node: Node) -> None:
        self.session.delete(node)
        self.session.flush()
