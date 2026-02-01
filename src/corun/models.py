"""Data models for Corun CLI."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Library metadata from metadata.json."""

    name: str
    version: str
    description: str
    library_id: str
    author: Optional[str] = None
    shells: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)


@dataclass
class Command:
    """A single command (shell script)."""

    name: str
    script_path: Path
    library_id: Optional[str] = None

    @property
    def is_standalone(self) -> bool:
        """Check if this is a standalone command."""
        return self.library_id is None


@dataclass
class Library:
    """A library containing multiple commands."""

    library_id: str
    path: Path
    metadata: Optional[Metadata] = None
    commands: list[Command] = field(default_factory=list)

    @property
    def name(self) -> str:
        """Get display name."""
        if self.metadata:
            return self.metadata.name
        return self.library_id

    @property
    def version(self) -> str:
        """Get version."""
        if self.metadata:
            return self.metadata.version
        return "unknown"

    @property
    def description(self) -> str:
        """Get description."""
        if self.metadata:
            return self.metadata.description
        return "No description"
