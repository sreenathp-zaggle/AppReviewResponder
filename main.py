from typing import List

from fastapi import FastAPI, Query, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

import database
from filters.FilterManager import FilterManager
from filters.ToxicityFilter import ToxicityFilter
from filters.PersonalInfoLeakageFilter import PersonalInfoLeakageFilter
from filters.SexualContentFilter import SexualContentFilter
from pipeline import ReviewPipeline
from uuid import UUID

from repository import schemas
from src.database import get_db
from src.repository import models

class ReviewData(BaseModel):
    user_id: UUID
    user_name: str = Field(..., min_length=2, max_length=100)
    reviewText: str = Field(..., min_length=5, max_length=5000)
    rating: int = Field(..., ge=1, le=5)

    @validator('reviewText')
    def review_text_not_empty(cls, review_text):
        if not review_text.strip():
            raise ValueError("Review text cannot be empty or just whitespace.")
        return review_text

    @validator('user_name')
    def username_not_blank(cls, user_name):
        if not user_name.strip():
            raise ValueError("Username must not be blank.")
        return user_name

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def get_filter_manager() -> FilterManager:
    filters = [ToxicityFilter()]
    return FilterManager(filters)

@app.post("/review/generate")
async def generate_response(review_data: ReviewData, db: Session = Depends(get_db), filter_manager: FilterManager = Depends(get_filter_manager)
):
    try:
        pipeline = ReviewPipeline(filter_manager)
        response = pipeline.run_pipeline_test(review_data, db)
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing review: {str(e)}")


@app.get("/listing/reviews", response_model=List[schemas.UserReview])
def get_reviews(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=20),
        db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    query = db.query(models.UserReview).outerjoin(models.ReviewResponseAI).filter(
        (models.UserReview.is_flagged == False) |
        ((models.UserReview.is_flagged == True) & (models.UserReview.moderation_status == 'approved'))
    )

    reviews = query.offset(skip).limit(size).all()

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found")

    return reviews