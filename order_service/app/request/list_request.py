from typing import Any
from pydantic import BaseModel


class Filters(BaseModel):
    column: str
    value: Any
    operator: str


class ListRequest(BaseModel):
    skip: int = 0
    limit: int = 100
    sort_by: str = 'id'
    sort: str = 'ASC'
    logic: str = 'and'
    filters: list[Filters]



