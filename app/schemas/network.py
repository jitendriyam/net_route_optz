from datetime import UTC, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class NodeCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=255)


class NodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class RouteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    source: str = Field(min_length=1, max_length=255)
    destination: str = Field(min_length=1, max_length=255)


class EdgeCreate(RouteRequest):
    latency: float = Field(gt=0, allow_inf_nan=False)


class EdgeResponse(BaseModel):
    id: int
    source: str
    destination: str
    latency: float


class RouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source_name: str
    destination_name: str
    total_latency: float
    path: list[str]
    created_at: datetime


class HistoryFilters(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    source: str | None = Field(default=None, min_length=1, max_length=255)
    destination: str | None = Field(default=None, min_length=1, max_length=255)
    limit: int = Field(default=100, ge=1, le=1000)
    date_from: datetime | None = None
    date_to: datetime | None = None

    @field_validator("date_from", "date_to")
    @classmethod
    def normalize_utc(cls, value):
        if value is None:
            return None
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_range(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be before or equal to date_to")
        return self
