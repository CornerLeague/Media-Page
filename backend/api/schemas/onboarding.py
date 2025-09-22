"""
Onboarding API request/response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class OnboardingStepUpdate(BaseModel):
    """Request schema for updating current onboarding step"""
    step: int = Field(..., ge=1, le=5, description="Onboarding step number (1-5)")

    @validator('step')
    def validate_step(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError('Step must be between 1 and 5')
        return v


class OnboardingStatusResponse(BaseModel):
    """Response schema for onboarding status"""
    is_onboarded: bool
    current_step: Optional[int]
    onboarding_completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class OnboardingSportResponse(BaseModel):
    """Response schema for sports in onboarding"""
    id: UUID
    name: str
    slug: str
    icon: Optional[str] = None
    icon_url: Optional[str] = None
    description: Optional[str] = None
    popularity_rank: int
    is_active: bool

    class Config:
        from_attributes = True


class OnboardingTeamResponse(BaseModel):
    """Response schema for teams in onboarding"""
    id: UUID
    name: str
    market: str
    slug: str
    sport_id: UUID
    logo_url: Optional[str] = None
    abbreviation: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    league_info: Optional[dict] = None

    class Config:
        from_attributes = True


class OnboardingSportsListResponse(BaseModel):
    """Response schema for sports list in onboarding"""
    sports: List[OnboardingSportResponse]
    total: int


class OnboardingTeamsListResponse(BaseModel):
    """Response schema for teams list in onboarding"""
    teams: List[OnboardingTeamResponse]
    total: int
    sport_ids: List[UUID]


class OnboardingCompletionRequest(BaseModel):
    """Request schema for completing onboarding"""
    # Optional: could include final preferences validation
    force_complete: bool = Field(default=False, description="Force completion even if preferences are incomplete")


class OnboardingCompletionResponse(BaseModel):
    """Response schema for onboarding completion"""
    success: bool
    user_id: UUID
    onboarding_completed_at: datetime
    message: str

    class Config:
        from_attributes = True