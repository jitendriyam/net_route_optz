from pydantic import BaseModel


class TestDataResponse(BaseModel):
    nodes: list[str]
    edges: list[dict[str, str | float]]
