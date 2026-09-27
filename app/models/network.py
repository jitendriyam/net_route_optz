from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from app.db.base import Base, utc_now


class Node(Base):
    __tablename__ = "nodes"
    __table_args__ = (UniqueConstraint("name", name="uq_nodes_name"),)

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class Edge(Base):
    __tablename__ = "edges"
    __table_args__ = (
        UniqueConstraint("source_id", "destination_id", name="uq_edges_source_destination"),
        CheckConstraint("latency > 0", name="ck_edges_positive_latency"),
    )

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    destination_id = Column(
        Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    latency = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class RouteHistory(Base):
    __tablename__ = "route_history"

    id = Column(Integer, primary_key=True)
    source_name = Column(String(255), nullable=False, index=True)
    destination_name = Column(String(255), nullable=False, index=True)
    total_latency = Column(Float, nullable=False)
    path = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
