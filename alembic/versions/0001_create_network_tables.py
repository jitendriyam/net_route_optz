"""create network tables

Revision ID: 0001_create_network_tables
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_create_network_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_nodes_name"),
    )
    op.create_table(
        "edges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("destination_id", sa.Integer(), nullable=False),
        sa.Column("latency", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["destination_id"], ["nodes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "source_id", "destination_id", name="uq_edges_source_destination"
        ),
        sa.CheckConstraint("latency > 0", name="ck_edges_positive_latency"),
    )
    op.create_index("ix_edges_destination_id", "edges", ["destination_id"])
    op.create_table(
        "route_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("destination_name", sa.String(length=255), nullable=False),
        sa.Column("total_latency", sa.Float(), nullable=False),
        sa.Column("path", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_route_history_source_name", "route_history", ["source_name"])
    op.create_index(
        "ix_route_history_destination_name", "route_history", ["destination_name"]
    )
    op.create_index("ix_route_history_created_at", "route_history", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_route_history_created_at", table_name="route_history")
    op.drop_index("ix_route_history_destination_name", table_name="route_history")
    op.drop_index("ix_route_history_source_name", table_name="route_history")
    op.drop_table("route_history")
    op.drop_index("ix_edges_destination_id", table_name="edges")
    op.drop_table("edges")
    op.drop_table("nodes")
