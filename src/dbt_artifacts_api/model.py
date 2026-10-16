from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ResourceType(StrEnum):
    MODEL = "model"
    SEED = "seed"
    SNAPSHOT = "snapshot"
    SOURCE = "source"
    TEST = "test"
    MACRO = "macro"


class Node(BaseModel):
    database: str
    schema_: str = Field(alias="schema")
    resource_type: ResourceType
    original_file_path: str
    package_name: str | None
    path: str
    materialized: str
    tags: list[str]
    name: str
    description: str
    unique_id: str
    created_at: datetime
    checksum: str


class Edge(BaseModel):
    parent: str
    child: str


class Invocation(BaseModel):
    invocation_id: str
    generated_at: str
    dbt_version: str
    target: str | None
    elapsed_time: float


class NodeResult(BaseModel):
    invocation_id: str
    unique_id: str
    status: str
    execution_time: float
    rows_affected: int
    bytes_processed: int
    message: str | None
