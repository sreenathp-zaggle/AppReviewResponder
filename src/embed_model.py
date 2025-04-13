import os

import openai
import pandas as pd
import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from database import get_db
from repository.models import FAQ

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to generate embeddings using OpenAI API
def get_embeddings(texts, model=EMBEDDING_MODEL):
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    embeddings = [item.embedding for item in response.data]
    return np.array(embeddings)

def save_faqs_to_db(df):
    db = next(get_db())
    for idx, row in df.iterrows():
        if pd.isna(row["UserQuery"]) or pd.isna(row["ProductResponses"]):
            continue
        db.add(FAQ(question=row["UserQuery"], answer=row["ProductResponses"]))
    db.commit()

def embed_faq(file_path="./data/Chatbot_FAQs_dataset.xlsx"):
    print("Entering embed_faq() model")

    # Read the FAQ dataset
    df = pd.read_excel(file_path)

    # Save FAQs to DB
    save_faqs_to_db(df)

    # Prepare data for embedding
    faq_data = []
    for idx, row in df.iterrows():
        if row["UserQuery"] is None or row["ProductResponses"] is None:
            continue
        content = f"Q: {row['UserQuery']} A: {row['ProductResponses']}"
        faq_data.append(content)

    # Generate embeddings using OpenAI
    embeddings = get_embeddings(faq_data)

    # Define the FAISS index (use dimension based on your embedding model size)
    dimension = embeddings.shape[1]  # Assuming embeddings are 2D (num_samples x embedding_dimension)
    index = faiss.IndexFlatL2(dimension)  # Using a simple L2 (Euclidean) distance index

    # Add embeddings to FAISS index
    index.add(embeddings)

    # Save the index to disk
    faiss.write_index(index, 'faq_index.faiss')

    print("✅ FAQ embedding completed.")

if __name__ == "__main__":
    embed_faq()