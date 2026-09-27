from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.network import RouteHistory


class RouteHistoryRepository:
    """Database access for persisted route results and their filters only."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        source_name: str,
        destination_name: str,
        total_latency: float,
        path: list[str],
    ) -> RouteHistory:
        history = RouteHistory(
            source_name=source_name,
            destination_name=destination_name,
            total_latency=total_latency,
            path=path,
        )
        self.session.add(history)
        self.session.flush()
        return history

    def filter(
        self,
        *,
        source_name: str | None = None,
        destination_name: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int | None = None,
    ) -> list[RouteHistory]:
        statement = select(RouteHistory)
        if source_name is not None:
            statement = statement.where(RouteHistory.source_name == source_name)
        if destination_name is not None:
            statement = statement.where(RouteHistory.destination_name == destination_name)
        if created_from is not None:
            statement = statement.where(RouteHistory.created_at >= created_from)
        if created_to is not None:
            statement = statement.where(RouteHistory.created_at <= created_to)
        statement = statement.order_by(RouteHistory.created_at.desc(), RouteHistory.id.desc())
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.scalars(statement))
