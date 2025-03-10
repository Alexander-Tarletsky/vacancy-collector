from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VacancyBase(BaseModel):
    message_id: str = Field(description="Telegram message ID")
    content: str | None
    contact: str | None
    is_viewed: bool = Field(default=False)
    is_opportunity: bool = Field(default=False)
    is_applied: bool = Field(default=False)
    is_rejected: bool = Field(default=False)


class VacancyCreate(VacancyBase):
    channel_id: UUID


class VacancyUpdate(BaseModel):
    is_viewed: bool | None


class VacancyResponse(VacancyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    channel_id: UUID

    model_config = ConfigDict(from_attributes=True)


# For Opportunities, since it is now handled by `is_opportunity` in Vacancy:
class OpportunityResponse(VacancyResponse):
    model_config = ConfigDict(from_attributes=True)
