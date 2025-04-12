import os
import pandas as pd
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
load_dotenv()
EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def embed_faq(file_path="./data/Chatbot_FAQs_dataset.xlsx"):
    print("Entering embed_faq() model")
    chroma_client = chromadb.PersistentClient(path='./chroma_db')
    embedding_fn = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name=EMBEDDING_MODEL)
    collection = chroma_client.get_or_create_collection(name="faq_embeddings", embedding_function=embedding_fn)

    if collection.count() > 0:
        print("✅ FAQ already embedded.")
        return

    df = pd.read_excel(file_path)
    for idx, row in df.iterrows():
        doc_id = f"faq_{idx}"
        if(row["UserQuery"] is None or row["ProductResponses"] is None):
            # print(f"Skipping row {idx} due to missing data.")
            continue

        content = f"Q: {row['UserQuery']} A: {row['ProductResponses']}"
        collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[{
                "question": row["UserQuery"],
                "answer": row["ProductResponses"]}]
        )

    print("✅ FAQ embedding completed.")

if __name__ == "__main__":
    embed_faq()