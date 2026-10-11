from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IssuePriority(StrEnum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class IssueStatus(StrEnum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class IssueCreate(BaseModel):
    # status is not accepted here, new issues always start as open
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    priority: IssuePriority


class IssueUpdate(BaseModel):
    # only status and priority can change, anything else is rejected
    model_config = ConfigDict(extra='forbid')

    status: IssueStatus | None = None
    priority: IssuePriority | None = None

    @model_validator(mode='after')
    def require_at_least_one_field(self) -> Self:
        if self.status is None and self.priority is None:
            raise ValueError('At least one of status or priority is required')
        return self


class Issue(BaseModel):
    id: str
    title: str
    description: str
    priority: IssuePriority
    status: IssueStatus
    created_by: str
    created_at: datetime
    updated_at: datetime


class IssuePage(BaseModel):
    items: list[Issue]
    next_cursor: str | None


class IssueSummary(BaseModel):
    total: int
    by_status: dict[IssueStatus, int]
