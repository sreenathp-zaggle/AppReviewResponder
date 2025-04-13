import faiss
import pandas as pd
import os
from dotenv import load_dotenv
from database import get_db
from embed_model import get_embeddings
from sqlalchemy.orm import Session
load_dotenv()
EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_relevant_faqs(review_text: str, db:Session, top_k=3):
    print("Entering search_faq() model")

    # Generate the embedding for the query
    query_embedding = get_embeddings([review_text])

    # Load the pre-built FAISS index
    index = faiss.read_index('faq_index.faiss')

    # Perform the search for the nearest neighbors
    distances, indices = index.search(query_embedding, top_k)

    df = pd.read_sql("SELECT question, answer FROM faqs", db.bind)

    results = []
    for idx in indices[0]:
        if idx != -1:
            results.append({
                "question": df.iloc[idx]["question"],
                "answer": df.iloc[idx]["answer"]
            })

    return results
