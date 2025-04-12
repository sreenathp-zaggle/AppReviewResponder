import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserReview(Base):
    __tablename__ = 'user_reviews'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    username = Column(String(255))
    review_text = Column(Text, nullable=False)
    rating = Column(Integer)

    # 🚩 New columns for moderation
    is_flagged = Column(Boolean, default=False)  # True if flagged
    flagged_by = Column(String, nullable=True, default='auto-moderation')   #auto-moderation or manual
    moderation_status = Column(String, default="pending")  # 'pending', 'approved', 'rejected'
    flagged_at = Column(DateTime(timezone=True), server_default=func.now())  # When it was flagged

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # When the review was created
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # When the review was last updated
    responses = relationship("ReviewResponseAI", back_populates="review", cascade="all, delete-orphan")

    # Indexing flagging and moderation columns for better performance on filters
    __table_args__ = (
        Index('ix_user_reviews_flagged', 'is_flagged', 'moderation_status'),
        Index('ix_user_reviews_flagged_by', 'flagged_by'),
        Index('ix_user_reviews_created_at', 'created_at'),
    )

class ReviewResponseAI(Base):
    __tablename__ = "review_responses_ai"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("user_reviews.id", ondelete="CASCADE"), nullable=False)
    responder_type = Column(String, default='ai')  # ai/manual/admin
    response_text = Column(Text, nullable=False)
    language = Column(String, default='en')

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    review = relationship("UserReview", back_populates="responses")

    # Indexing review_id for performance, since this is likely used frequently in queries
    __table_args__ = (
        Index('ix_review_responses_ai_review_id', 'review_id'),
    )