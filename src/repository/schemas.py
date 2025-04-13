from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


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
    created_at: datetime
    responses: Optional[List[ReviewResponseAI]]

    class Config:
        orm_mode = True