#This file will hold Pydantic model for the SilverRecord

from pydantic import BaseModel, Field
from typing import Dict, Any

class SilverRecord(BaseModel):
    """
    Standardized schema for all cleaned document records across
    Notion, Obsidian, and Github sources.
    """

    id: str = Field(..., description="Unique source-specific ID")
    type: str = Field(..., description="Document type (e.g., page, note, markdown)")
    text: str = Field(..., description="Normalized text content")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last modified timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source-specific metadata")
    