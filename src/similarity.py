import numpy as np
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

import chromadb
load_dotenv()
EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def find_similar_faq(user_input, faq_questions, faq_embeddings, embed_model, top_k=1):
    user_vec = embed_model.encode([user_input])
    scores = cosine_similarity(user_vec, faq_embeddings)[0]
    best_idx = scores.argsort()[-top_k:][::-1]
    return [faq_questions[i] for i in best_idx], [scores[i] for i in best_idx], best_idx

chroma_client = chromadb.PersistentClient(path='./chroma_db')
embedding_fn = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name=EMBEDDING_MODEL)
collection = chroma_client.get_collection(name ="faq_embeddings")

def get_relevant_faqs(review_text: str):
    print("Review text:", review_text)
    embedded = embedding_fn([review_text])[0]
    results = collection.query(query_embeddings=[embedded], n_results=3)

    if not results["documents"]:
        return []
    print("Results:", results["metadatas"])
    faqs = [
        {"question": m["question"],
         "answer": m["answer"] if "answer" in m else None,
         "text": d}
        for m, d in zip(results["metadatas"][0], results["documents"][0])]
    return faqs