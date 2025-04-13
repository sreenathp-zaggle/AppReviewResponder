from datetime import datetime
from enum import Enum
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from pydantic import BaseModel, validator
from uuid import UUID

IST = timezone(timedelta(hours=5, minutes=30))

class ModerationStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ReviewResponseAI(BaseModel):
    id: UUID
    response_text: str
    responder_type: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserReview(BaseModel):
    id: UUID
    review_text: str
    username: str
    rating: int
    is_flagged: bool
    moderation_status: Optional[str]
    created_at: datetime
    responses: Optional[List[ReviewResponseAI]]

    class Config:
        orm_mode = True

class GroupedReviews(BaseModel):
    user: List[UserReview]
    admin: List[UserReview]

class ReviewModerationUpdateRequest(BaseModel):
    review_id: UUID
    moderation_status: ModerationStatusEnum




