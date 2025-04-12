from transformers import pipeline

classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment")

label_map = {
    'LABEL_0': 'negative',
    'LABEL_1': 'neutral',
    'LABEL_2': 'positive'
}

def classify_sentiment(text):
    result = classifier(text)
    label = result[0]['label']
    sentiment = label_map.get(label, 'neutral') # 'positive', 'negative', or 'neutral'
    return sentiment

def classify_input_rating(text):
    if text >= 4:
        return 'positive'
    elif text == 3:
        return 'neutral'
    else:
        return 'negative'