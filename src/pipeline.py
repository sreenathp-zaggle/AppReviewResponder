import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from filters.FilterManager import FilterManager
from generator import generate_response
from sentiment import classify_sentiment, classify_input_rating
from similarity import get_relevant_faqs
from src.repository.models import UserReview, ReviewResponseAI

logger = logging.getLogger(__name__)


def _handle_flagged_review(db, review_data, flagged_reason, custom_response_text):
    flagged_review = UserReview(
        review_text=review_data.reviewText,
        rating=review_data.rating,
        user_id=review_data.user_id,
        username=review_data.user_name,
        is_flagged=True,
        flagged_by=flagged_reason,
        moderation_status='pending',
    )
    db.add(flagged_review)
    db.commit()
    logger.info(f"Flagged review for user_id={review_data.user_id}. Reason: {flagged_reason}")
    return custom_response_text or "Thanks for your feedback. A member of our support team will review your message."


def _store_valid_review(db, review_data, response_text: str) -> str:
    review = UserReview(
        review_text=review_data.reviewText,
        user_id=review_data.user_id,
        username=review_data.user_name,
        rating=review_data.rating
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    response = ReviewResponseAI(
        review_id=review.id,
        responder_type="ai",
        response_text=response_text,
        language="en"
    )
    db.add(response)
    db.commit()

    logger.info(f"Review successfully stored for user_id={review_data.user_id}")
    return response_text


def build_contradiction_prompt(review_data) -> str:
    """
    Build prompt when the star rating and review tone conflict.
    """
    return (
        f'The review rating and sentiment don\'t match. The user gave a "{review_data.rating}" star but wrote this:\n'
        f'"{review_data.reviewText}".\n\n'
        f'Respond empathetically, acknowledging both parts of the feedback. '
        f'Ask if they need support and offer help if needed.'
    )


def build_prompt_by_sentiment(sentiment: str, review_data) -> str:
    """
    Build appropriate prompt based on sentiment.
    """
    if sentiment == 'negative':
        relevant_faqs = get_relevant_faqs(review_data.reviewText)
        faq_text = "\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in relevant_faqs])
        return (
            f'You are a friendly support assistant. Respond empathetically to this user review: '
            f'"{review_data.reviewText}".\nUse this info from our FAQ to help:\n"{faq_text}"\n\n'
            f'Here is the email of care team - care@zaggle.in.'
        )

    elif sentiment == 'positive':
        return (
            f'Thank the user for their positive review: "{review_data.reviewText}". '
            f'Encourage them to explore more features of the app.'
        )

    else:  # Neutral
        return (
            f'Acknowledge this neutral review: "{review_data.reviewText}". '
            f'Offer helpful advice or thank the user.'
        )


class ReviewPipeline:
    def __init__(self, filter_manager: FilterManager):
        self.filter_manager = filter_manager

    def run_pipeline_test(self, review_data, db:Session) -> str:
        try:
            is_flagged, flagged_reason, custom_response = self.filter_manager.apply_filters(review_data.reviewText)

            if is_flagged:
                return _handle_flagged_review(db, review_data, flagged_reason, custom_response)

            input_rating_sentiment = classify_input_rating(review_data.rating)
            ai_sentiment = classify_sentiment(review_data.reviewText)

            if input_rating_sentiment == ai_sentiment:
                prompt = build_prompt_by_sentiment(ai_sentiment, review_data)
            else:
                prompt = build_contradiction_prompt(review_data)

            response_text = generate_response(prompt)

            response = _store_valid_review(db, review_data, response_text)
            logger.info(f"AI response saved for user_id={review_data.user_id}")
            return response

        except Exception as e:
            logger.error(f"Error processing review for user_id={review_data.user_id}: {str(e)}", exc_info=True)
            raise

