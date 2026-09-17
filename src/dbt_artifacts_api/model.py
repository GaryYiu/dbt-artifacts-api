from pydantic import BaseModel, Field
from datetime import datetime

class Node(BaseModel):
    database: str
    schema_: str = Field(alias="schema")
    resource_type: str
    original_file_path: str
    unique_id: str
    description: str
    created_at: datetime
    
