from transformers import pipeline

from filters.ContentFilter import ContentFilter

class SexualContentFilter(ContentFilter):
    def __init__(self):
        self.classifier = pipeline("text-classification", model="erax-ai/EraX-Anti-NSFW-V1.1")
        self.latest_score = 0.0
        self.latest_label = ""

    def check(self, review_text: str) -> bool:
        result = self.classifier(review_text)
        self.latest_label = result[0]["label"].lower()
        self.latest_score = result[0]["score"]
        return self.latest_label in ["nsfw", "sexual_explicit"] and self.latest_score > 0.60

    def reason(self) -> str:
        return "Sexual/NSFW"

    def generate_response_based_on_confidence(self) -> str:
        if self.latest_score > 0.90:
            return "Your message contains inappropriate or sexually explicit language and cannot be processed."
        elif self.latest_score > 0.70:
            return "Your feedback includes potentially explicit content. A support member will review it before we respond."
        else:
            return "Thanks for your feedback. A member of our support team will review your message."