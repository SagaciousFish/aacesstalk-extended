from typing import Optional, Literal
from datetime import datetime

from sqlmodel import SQLModel, Column, JSON, Field, Relationship
from sqlalchemy import DateTime, func

from py_core.system.model import id_generator, DialogueRole
from chatlib.utils.time import get_timestamp


class BaseTable:
    id: str = Field(primary_key=True, default_factory=id_generator)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True),
                         server_default=func.now(), nullable=True)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True),
                         server_default=func.now(),
                         onupdate=func.now(), nullable=True)
    )


class Parent(SQLModel, table=True, BaseTable):
    role: Literal[DialogueRole.Parent] = DialogueRole.Parent

    name: str = Field(index=True)

    children: list['Child'] = Relationship(back_populates='parent')

    sessions: list['Session'] = Relationship(back_populates='parent')


class Child(SQLModel, table=True, BaseTable):
    role: Literal[DialogueRole.Child] = DialogueRole.Child

    name: str = Field(index=True)

    parent_id: Optional[str] = Field(default=None, foreign_key='parent.id')
    parent: Optional[Parent] = Relationship(back_populates="children")

    sessions: list['Session'] = Relationship(back_populates='child')


class Session(SQLModel, table=True, BaseTable):
    parent_id: str = Field(foreign_key='parent.id')
    child_id: str = Field(foreign_key='child.id')

    parent: Optional[Parent] = Relationship(back_populates="sessions")
    child: Optional[Child] = Relationship(back_populates="sessions")

    local_timezone: str = Field(nullable=False)
    started_timestamp: int = Field(default_factory=get_timestamp)
    ended_timestamp: int | None = None

