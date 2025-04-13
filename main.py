from typing import List

from fastapi import FastAPI, Query, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session

from filters.FilterManager import FilterManager
from filters.ToxicityFilter import ToxicityFilter
from filters.PersonalInfoLeakageFilter import PersonalInfoLeakageFilter
from filters.ObsceneContentFilter import ObsceneContentFilter
from pipeline import ReviewPipeline
from uuid import UUID
from fastapi.middleware.cors import CORSMiddleware
from repository import schemas
from repository.schemas import GroupedReviews
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

origins = [
    "http://localhost:5173",  # Vite frontend
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Optional, if you're using another port
    "https://<your-ngrok-url>.ngrok-free.app"  # Optional, if testing via ngrok
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # You can also set to ["*"] for all origins (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

def get_filter_manager() -> FilterManager:
    filters = [ToxicityFilter(), ObsceneContentFilter(), PersonalInfoLeakageFilter()]
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


@app.get("/listing/reviews", response_model=GroupedReviews)
def get_reviews(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    skip = (page - 1) * size

    all_reviews = (db.query(models.UserReview).outerjoin(models.ReviewResponseAI)
                   .order_by(desc(models.UserReview.created_at))
                   .offset(skip).limit(size).all())

    user_reviews = []
    admin_reviews = []

    for review in all_reviews:
        if not review.is_flagged or (review.is_flagged and review.moderation_status == 'approved'):
            user_reviews.append(review)
        elif review.is_flagged and review.moderation_status == 'rejected':
            continue
        else:
            admin_reviews.append(review)

    if not user_reviews and not admin_reviews:
        raise HTTPException(status_code=404, detail="No reviews found")

    return {
        "user": user_reviews,
        "admin": admin_reviews
    }

@app.post("/review/moderation_update")
def moderate_review(request: schemas.ReviewModerationUpdateRequest, db: Session = Depends(get_db)):
    review = db.query(models.UserReview).filter(models.UserReview.id == request.review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.moderation_status = request.moderation_status
    db.commit()
    db.refresh(review)
    return {"message": f"Review {request.moderation_status} successfully"}
