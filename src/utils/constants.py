TOXIC_RESPONSES = {
    "high": "This review contains extremely toxic language and cannot be processed. We encourage respectful communication and appreciate your understanding. Our team will review it shortly.",
    "moderate": "We’ve noticed some language in your review that may be considered inappropriate. While we are unable to process it right now, a support team member will review it and provide guidance.",
    "low": "Thanks for your feedback. A member of our support team will review your message.",
}

SENTIMENT_CLASSIFIER_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
NER_MODEL_NAME = "Jean-Baptiste/roberta-large-ner-english"
Obscene_MODEL_NAME = "uget/sexual_content_dection"
TOXIC_MODEL_NAME = "unitary/toxic-bert"
PERSONAL_ENTITY_LABELS = {"PER", "LOC", "ORG"}

STRUCTURED_INFO_PATTERNS = {
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone": r"\b(?:\+91[\-\s]?)?[789]\d{9}\b",
    "aadhaar": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "pan": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b"
}

NER_RESPONSES = {
    "high": "Your message contains sensitive personal information like '{entity}', and cannot be processed.",
    "medium": "Your feedback includes personal information like '{entity}'. A support member will review it before we respond.",
    "low": "Please avoid sharing personal or sensitive information in your review."
}

OBSCENE_RESPONSES = {
    "high": "Your message contains inappropriate or obscene explicit language and cannot be processed.",
    "medium": "Your feedback includes potentially explicit content. A support member will review it before we respond.",
    "low": "Thanks for your feedback. A member of our support team will review your message."
}

LABEL_MAP = {
    'LABEL_0': 'negative',
    'LABEL_1': 'neutral',
    'LABEL_2': 'positive'
}