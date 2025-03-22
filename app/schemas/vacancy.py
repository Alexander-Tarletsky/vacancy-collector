from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VacancyBase(BaseModel):
    content: str
    contact: str | None = Field(default=None)
    is_viewed: bool = Field(default=False)
    is_opportunity: bool = Field(default=False)
    is_applied: bool = Field(default=False)
    is_rejected: bool = Field(default=False)


class VacancyCreate(VacancyBase):
    message_id: str = Field(description="Telegram message ID")
    channel_id: UUID


class VacancyUpdate(VacancyBase):
    content: str | None = Field(default=None)


class VacancyResponse(VacancyBase):
    id: UUID
    message_id: str
    created_at: datetime
    updated_at: datetime
    channel_id: UUID

    model_config = ConfigDict(from_attributes=True)


# For Opportunities, since it is now handled by `is_opportunity` in Vacancy:
class OpportunityResponse(VacancyResponse):
    model_config = ConfigDict(from_attributes=True)
