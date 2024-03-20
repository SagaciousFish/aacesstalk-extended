from enum import StrEnum
from typing import Optional, Literal, Union
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Column, Field, Relationship, JSON
from sqlalchemy import DateTime, func, DATETIME

from py_core.system.model import (id_generator, DialogueRole, DialogueMessage as _DialogueMessage,
                                  CardInfoListTypeAdapter, CardInfo,
                                  ChildCardRecommendationResult as _ChildCardRecommendationResult,
                                  ParentGuideRecommendationResult as _ParentGuideRecommendationResult,
                                  ParentGuideElement)
from chatlib.utils.time import get_timestamp


class IdTimestampMixin(BaseModel):
    id: str = Field(primary_key=True, default_factory=id_generator)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_type= DateTime(timezone=True),
        sa_column_kwargs=dict(server_default=func.now(), nullable=True)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_type= DateTime(timezone=True),
        sa_column_kwargs=dict(server_default=func.now(), onupdate=func.now(), nullable=True)
    )


class Parent(SQLModel, IdTimestampMixin, table=True):

    name: str = Field(index=True)

    children: list['Child'] = Relationship(back_populates='parent')

    sessions: list['Session'] = Relationship(back_populates='parent')


class Child(SQLModel, IdTimestampMixin, table=True):

    name: str = Field(index=True)

    parent_id: Optional[str] = Field(default=None, foreign_key='parent.id')
    parent: Optional[Parent] = Relationship(back_populates="children")

    sessions: list['Session'] = Relationship(back_populates='child')


class Session(SQLModel, IdTimestampMixin, table=True):
    parent_id: str = Field(foreign_key='parent.id')
    child_id: str = Field(foreign_key='child.id')

    parent: Optional[Parent] = Relationship(back_populates="sessions")
    child: Optional[Child] = Relationship(back_populates="sessions")

    local_timezone: str = Field(nullable=False)
    started_timestamp: int = Field(default_factory=get_timestamp, index=True)
    ended_timestamp: int | None = Field(default=None, index=True)


class DialogueMessageContentType(StrEnum):
    text="text"
    json="json"

class DialogueMessage(SQLModel, IdTimestampMixin, table=True):
    session_id:str = Field(foreign_key="session.id")
    role: DialogueRole
    content_type: DialogueMessageContentType
    content_str: str
    timestamp: int = Field(default_factory=get_timestamp, index=True)
    recommendation_id: Optional[str] = Field(default=None)

    def to_data_model(self) -> _DialogueMessage:
        return _DialogueMessage(
            id=self.id,
            timestamp=self.timestamp,
            role=self.role,
            content=self.content_str if self.content_type == DialogueMessageContentType.text else CardInfoListTypeAdapter.validate_json(
                self.content_str),
            recommendation_id=self.recommendation_id
        )

    @classmethod
    def from_data_model(cls, session_id: str, message: _DialogueMessage) -> 'DialogueMessage':
        return DialogueMessage(
            **message.model_dump(),
            session_id=session_id,
            content_str=message.content if isinstance(message.content, str) else CardInfoListTypeAdapter.dump_json(
                message.content),
            content_type=DialogueMessageContentType.text if isinstance(message.content, str) else DialogueMessageContentType.json
        )


class ChildCardRecommendationResult(SQLModel, IdTimestampMixin, table=True):
    session_id:str = Field(foreign_key="session.id")
    timestamp: int = Field(default_factory=get_timestamp, index=True)
    cards: list[CardInfo] = Field(sa_column=Column(JSON), default=[])

    def to_data_model(self) -> _ChildCardRecommendationResult:
        return _ChildCardRecommendationResult(**self.model_dump())

    @classmethod
    def from_data_model(cls, session_id: str, data_model: _ChildCardRecommendationResult) -> 'ChildCardRecommendationResult':
        return ChildCardRecommendationResult(**data_model.model_dump(), session_id=session_id)


class ParentGuideRecommendationResult(SQLModel, IdTimestampMixin, table=True):
    session_id:str = Field(foreign_key="session.id")
    timestamp: int = Field(default_factory=get_timestamp, index=True)
    recommendations: list[ParentGuideElement] = Field(sa_column=Column(JSON), default=[])

    def to_data_model(self) -> _ParentGuideRecommendationResult:
        return _ParentGuideRecommendationResult(**self.model_dump())

    @classmethod
    def from_data_model(cls, session_id: str, data_model: _ParentGuideRecommendationResult) -> 'ParentGuideRecommendationResult':
        return ParentGuideRecommendationResult(**data_model.model_dump(), session_id=session_id)
