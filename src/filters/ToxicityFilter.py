from transformers import pipeline

from filters.ContentFilter import ContentFilter
from utils.constants import TOXIC_RESPONSES, TOXIC_MODEL_NAME


class ToxicityFilter(ContentFilter):
    def __init__(self):
        self.classifier = pipeline("text-classification", model=TOXIC_MODEL_NAME)
        self.latest_score = 0.0
        self.latest_label = ""

    def check(self, review_text: str) -> bool:
        result = self.classifier(review_text)
        self.latest_label = result[0]['label']
        self.latest_score = result[0]['score']
        return self.latest_label == "toxic" and self.latest_score > 0.60

    def reason(self) -> str:
        return "Hate Speech/Toxic"

    def generate_response_based_on_confidence(self) -> str:
        if self.latest_score > 0.90:
            return TOXIC_RESPONSES["high"]
        elif self.latest_score > 0.75:
            return TOXIC_RESPONSES["moderate"]
        else:
            return TOXIC_RESPONSES["low"]
