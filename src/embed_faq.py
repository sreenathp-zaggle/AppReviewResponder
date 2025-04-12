import pandas as pd
from sentence_transformers import SentenceTransformer

sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_faq(faq_path):
    df = pd.read_excel(faq_path)
    questions = df['UserQuery'].tolist()
    embeddings = sentence_model.encode(questions)
    return questions, embeddings, df

if __name__ == "_main_":
    embed_faq("./data/Chatbot_FAQs_dataset.xlsx")