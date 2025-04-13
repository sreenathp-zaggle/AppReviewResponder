from transformers import pipeline

from utils.constants import SENTIMENT_CLASSIFIER_MODEL, LABEL_MAP

classifier = pipeline("text-classification", model=SENTIMENT_CLASSIFIER_MODEL)



def classify_sentiment(text):
    result = classifier(text)
    label = result[0]['label']
    sentiment = LABEL_MAP.get(label, 'neutral') # 'positive', 'negative', or 'neutral'
    return sentiment

def classify_input_rating(text):
    if text >= 4:
        return 'positive'
    elif text == 3:
        return 'neutral'
    else:
        return 'negative'