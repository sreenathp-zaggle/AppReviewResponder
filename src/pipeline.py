import logging
from typing import List, Dict
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

def format_faq(faqs: List[Dict[str, str]]) -> str:
    return "\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in faqs])


def build_contradiction_prompt(review_data, db) -> str:
    """
    Builds a refined prompt when there's a mismatch between rating and review sentiment.
    If FAQ entries are relevant, they’re added into the response to support the user effectively.
    """
    review_text = review_data.reviewText
    rating = review_data.rating

    relevant_faqs = get_relevant_faqs(review_text, db)
    faq_text = ""
    if relevant_faqs:
        top_faq = relevant_faqs[0]  # Use top match for clarity
        faq_text = f'Here’s something that might help:\nQ: {top_faq["question"]}\nA: {top_faq["answer"]}'

    base_prompt = (
        f'The user gave a {rating}-star rating but wrote this:\n"{review_text}"\n\n'
        f'Respond warmly and acknowledge the mismatch. '
        f'If the review seems like a question or request for help, provide an appropriate answer.'
    )

    closing_line = "Invite them to reach out if they need more assistance at care@zaggle.in."

    return f"{base_prompt}\n\n{faq_text if faq_text else ''}\n\n{closing_line}"

def build_prompt_by_sentiment(sentiment: str, review_data, db) -> str:
    review_text = review_data.reviewText
    relevant_faqs = get_relevant_faqs(review_data.reviewText, db)

    if sentiment == 'negative':
        faq_text = format_faq(relevant_faqs) if relevant_faqs else ""
        return (
            f"You are a friendly support assistant. Respond empathetically to this user review: \"{review_text}\".\n"
            f"Use this info from our FAQ to help:\n{faq_text}\n\n"
            f"Include the care team email in your response: care@zaggle.in."
        )
    elif sentiment == 'positive':
        return (
            f"Thank the user for their positive review: \"{review_text}\". "
            f"Encourage them to explore more features of the app."
        )
    else:
        if relevant_faqs:
            faq_text = format_faq(relevant_faqs)
            return (
                f"Acknowledge this neutral review: \"{review_text}\".\n"
                f"Provide a helpful and informative reply based on this FAQ info:\n{faq_text}\n"
                f"Close with a polite tone."
            )
        else:
            return (
                f"Acknowledge this neutral review: \"{review_text}\". "
                f"Offer helpful advice or thank the user."
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
                prompt = build_prompt_by_sentiment(ai_sentiment, review_data, db)
            else:
                prompt = build_contradiction_prompt(review_data, db)

            response_text = generate_response(prompt)

            response = _store_valid_review(db, review_data, response_text)
            logger.info(f"AI response saved for user_id={review_data.user_id}")
            return response

        except Exception as e:
            logger.error(f"Error processing review for user_id={review_data.user_id}: {str(e)}", exc_info=True)
            raise

