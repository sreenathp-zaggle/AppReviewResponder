from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from filters.ContentFilter import ContentFilter
from utils.constants import Obscene_MODEL_NAME, OBSCENE_RESPONSES

class ObsceneContentFilter(ContentFilter):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(Obscene_MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(Obscene_MODEL_NAME)
        self.latest_score = 0.0
        self.latest_label = ""

    def check(self, review_text: str) -> bool:
        inputs = self.tokenizer(review_text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.sigmoid(outputs.logits)
            prediction = torch.argmax(probs, dim=-1).item()
            self.latest_score = probs[0][1].item()  # Score for class 1 (Obscene)
            self.latest_label = "Obscene" if prediction == 1 else "none"
        return prediction == 1 and self.latest_score > 0.60

    def reason(self) -> str:
        return "Obscene/NSFW"

    def generate_response_based_on_confidence(self) -> str:
        if self.latest_score > 0.90:
            return OBSCENE_RESPONSES["high"]
        elif self.latest_score > 0.75:
            return OBSCENE_RESPONSES["medium"]
        else:
            return OBSCENE_RESPONSES["low"]