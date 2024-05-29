from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from nanoid import generate
from sqlalchemy import DateTime, func

class DyadLoginCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, default_factory=lambda: generate("0123456789", 6))
    issued_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs=dict(server_default=func.now(), nullable=True)
    )
    active: bool = Field(default=True)
    dyad_id: str = Field(foreign_key="dyad.id")
