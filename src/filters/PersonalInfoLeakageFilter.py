from transformers import pipeline
import re
from filters.ContentFilter import ContentFilter
from utils.constants import NER_MODEL_NAME, PERSONAL_ENTITY_LABELS, NER_RESPONSES, STRUCTURED_INFO_PATTERNS

class PersonalInfoLeakageFilter(ContentFilter):
    def __init__(self):
        self.ner_pipeline = pipeline(
            "ner",
            model=NER_MODEL_NAME,
            tokenizer=NER_MODEL_NAME,
            aggregation_strategy="simple"  # Merges subwords like "Joh" + "n" = "John"
        )
        self.latest_score = 0.0
        self.latest_entity = ""

    def check(self, review_text: str) -> bool:
        if self.contains_structured_info(review_text):
            return True

        named_entities = self.ner_pipeline(review_text)

        for entity in named_entities:
            if entity['entity_group'] in PERSONAL_ENTITY_LABELS and entity['score'] > 0.75:
                self.latest_entity = entity['word']
                self.latest_score = entity['score']
                return True

        return False

    def reason(self) -> str:
        return "Personal Info Leakage"

    def generate_response_based_on_confidence(self) -> str:
        if self.latest_score > 0.90:
            return NER_RESPONSES["high"].format(entity=self.latest_entity)
        elif self.latest_score > 0.75:
            return NER_RESPONSES["medium"].format(entity=self.latest_entity)
        else:
            return NER_RESPONSES["low"]

    def contains_structured_info(self, text: str) -> bool:
        for pattern in STRUCTURED_INFO_PATTERNS.values():
            if re.search(pattern, text):
                return True
        return False
