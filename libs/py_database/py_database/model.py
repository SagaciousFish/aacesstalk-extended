from enum import StrEnum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Column, Field, Relationship, JSON
from sqlalchemy import DateTime, func

from py_core.system.model import (id_generator, DialogueRole, DialogueMessage as _DialogueMessage,
                                  CardInfoListTypeAdapter, CardInfo,
                                  ChildCardRecommendationResult as _ChildCardRecommendationResult,
                                  InterimCardSelection as _InterimCardSelection,
                                  ParentGuideRecommendationResult as _ParentGuideRecommendationResult,
                                  ParentGuideElement,
                                  ParentType,
                                  ParentExampleMessage as _ParentExampleMessage, CardIdentity,
                                  Session as _Session,
                                  Dyad as _Dyad
                                  )
from py_core.system.session_topic import SessionTopicCategory, SessionTopicInfo
from chatlib.utils.time import get_timestamp


class IdTimestampMixin(BaseModel):
    id: str = Field(primary_key=True, default_factory=id_generator)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs=dict(server_default=func.now(), nullable=True)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs=dict(server_default=func.now(), onupdate=func.now(), nullable=True)
    )


class Dyad(SQLModel, IdTimestampMixin, table=True):
    alias: str = Field(min_length=1, unique=True)
    child_name: str = Field(min_length=1)
    parent_type: ParentType = Field(nullable=False)

    sessions: list['Session'] = Relationship(back_populates='dyad')

    def to_data_model(self) -> _Dyad:
        return _Dyad(id=self.id, alias=self.alias, parent_type=self.parent_type)


class Session(SQLModel, IdTimestampMixin, table=True):
    dyad_id: str = Field(foreign_key=f"dyad.id")

    dyad: Dyad = Relationship(back_populates="sessions")
    
    topic_category: SessionTopicCategory
    subtopic: Optional[str] = None
    subtopic_description: Optional[str] = None

    local_timezone: str = Field(nullable=False)
    started_timestamp: int = Field(default_factory=get_timestamp, index=True)
    ended_timestamp: int | None = Field(default=None, index=True)

    def to_data_model(self) -> _Session:
        return _Session(
            id=self.id,
            topic=SessionTopicInfo(category=self.topic_category, subtopic=self.subtopic, subtopic_description=self.subtopic_description),
            local_timezone=self.local_timezone,
            started_timestamp=self.started_timestamp,
            ended=self.ended_timestamp
        )
    
    @classmethod
    def from_data_model(cls, session_info: _Session, dyad_id: str) -> 'Session':
        return Session(**session_info.model_dump(exclude={'topic'}),
                    dyad_id=dyad_id,
                    topic_category=session_info.topic.category,
                    subtopic=session_info.topic.subtopic,
                    subtopic_description=session_info.topic.subtopic_description
                    )


class SessionIdMixin(BaseModel):
    session_id: str = Field(foreign_key=f"{Session.__tablename__}.id")


class TimestampColumnMixin(BaseModel):
    timestamp: int = Field(default_factory=get_timestamp, index=True)


class DialogueMessageContentType(StrEnum):
    text = "text"
    json = "json"


class DialogueMessage(SQLModel, IdTimestampMixin, SessionIdMixin, table=True):
    role: DialogueRole
    content_type: DialogueMessageContentType
    content_str_localized: Optional[str] = Field(default=None)
    content_str: str = Field(nullable=False, min_length=1)
    timestamp: int = Field(default_factory=get_timestamp, index=True)
    recommendation_id: Optional[str] = Field(default=None)

    def to_data_model(self) -> _DialogueMessage:
        return _DialogueMessage(
            id=self.id,
            timestamp=self.timestamp,
            role=self.role,
            content=self.content_str if self.content_type == DialogueMessageContentType.text else CardInfoListTypeAdapter.validate_json(
                self.content_str),
            content_localized=self.content_str_localized,
            recommendation_id=self.recommendation_id
        )

    @classmethod
    def from_data_model(cls, session_id: str, message: _DialogueMessage) -> 'DialogueMessage':
        return DialogueMessage(
            **message.model_dump(),
            session_id=session_id,
            content_str_localized=message.content_localized,
            content_str=message.content if isinstance(message.content, str) else CardInfoListTypeAdapter.dump_json(
                message.content),
            content_type=DialogueMessageContentType.text if isinstance(message.content,
                                                                       str) else DialogueMessageContentType.json
        )


class ChildCardRecommendationResult(SQLModel, IdTimestampMixin, SessionIdMixin, TimestampColumnMixin, table=True):
    cards: list[CardInfo] = Field(sa_column=Column(JSON), default=[])

    def to_data_model(self) -> _ChildCardRecommendationResult:
        return _ChildCardRecommendationResult(**self.model_dump())

    @classmethod
    def from_data_model(cls, session_id: str,
                        data_model: _ChildCardRecommendationResult) -> 'ChildCardRecommendationResult':
        return ChildCardRecommendationResult(**data_model.model_dump(), session_id=session_id)


class InterimCardSelection(SQLModel, IdTimestampMixin, SessionIdMixin, TimestampColumnMixin, table=True):
    cards: list[CardIdentity] = Field(sa_column=Column(JSON), default=[])

    def to_data_model(self) -> _InterimCardSelection:
        return _InterimCardSelection(**self.model_dump())

    @classmethod
    def from_data_model(cls, session_id: str, data_model: _InterimCardSelection) -> 'InterimCardSelection':
        return InterimCardSelection(**data_model.model_dump(), session_id=session_id)


class ParentGuideRecommendationResult(SQLModel, IdTimestampMixin, SessionIdMixin, TimestampColumnMixin, table=True):
    guides: list[ParentGuideElement] = Field(sa_column=Column(JSON), default=[])

    def to_data_model(self) -> _ParentGuideRecommendationResult:
        return _ParentGuideRecommendationResult(**self.model_dump())

    @classmethod
    def from_data_model(cls, session_id: str,
                        data_model: _ParentGuideRecommendationResult) -> 'ParentGuideRecommendationResult':
        return ParentGuideRecommendationResult(**data_model.model_dump(), session_id=session_id)


class ParentExampleMessage(SQLModel, IdTimestampMixin, SessionIdMixin, table=True):
    recommendation_id: str = Field(foreign_key=f"{ParentGuideRecommendationResult.__tablename__}.id")
    guide_id: str = Field(nullable=False, index=True)

    message: str = Field(nullable=False)
    message_localized: Optional[str] = Field(default=None)

    def to_data_model(self) -> _ParentExampleMessage:
        return _ParentExampleMessage(**self.model_dump())

    @classmethod
    def from_data_model(cls, session_id: str, data_model: _ParentExampleMessage) -> 'ParentExampleMessage':
        return ParentExampleMessage(**data_model.model_dump(), session_id=session_id)
