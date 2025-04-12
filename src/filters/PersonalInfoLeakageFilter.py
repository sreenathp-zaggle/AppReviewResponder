from transformers import pipeline
import re
from filters.ContentFilter import ContentFilter

ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

class PersonalInfoLeakageFilter(ContentFilter):
    def __init__(self):
        self.ner_pipeline = pipeline(
            "ner",
            model="Jean-Baptiste/roberta-large-ner-english",
            tokenizer="Jean-Baptiste/roberta-large-ner-english",
            aggregation_strategy="simple"  # Merges subwords like "Joh" + "n" = "John"
        )

    def check(self, review_text: str) -> bool:
        if self.contains_structured_info(review_text):
            return True

        named_entities = self.ner_pipeline(review_text)
        personal_entity_labels = {"PER", "LOC", "ORG"}

        for entity in named_entities:
            if entity['entity_group'] in personal_entity_labels and entity['score'] > 0.75:
                return True

        return False

    def contains_structured_info(self, text: str) -> bool:
        # Regex patterns for structured info
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        phone_pattern = r"\b(?:\+91[\-\s]?)?[789]\d{9}\b"
        aadhaar_pattern = r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
        pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

        patterns = [email_pattern, phone_pattern, aadhaar_pattern, pan_pattern]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    def reason(self) -> str:
        return "Personal Info Leakage"

    def generate_response_based_on_confidence(self) -> str:
        return "Please avoid sharing personal or sensitive information in your review."
