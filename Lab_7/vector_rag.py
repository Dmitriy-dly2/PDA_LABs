import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


def load_data(model_type="minilm"):
    with open("models/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    with open(f"models/embeddings_{model_type}.pkl", "rb") as f:
        embeddings = pickle.load(f)

    return chunks, embeddings


def build_index(embeddings):
    emb = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(emb.shape[1])
    index.add(emb)
    return index


def retrieve(query, index, chunks, model, k=3):
    q = model.encode([query]).astype("float32")
    _, idx = index.search(q, k)
    return [chunks[i] for i in idx[0]]


if __name__ == "__main__":
    print("Testing retrieval...")

    for model_type in ["minilm", "mpnet"]:
        print(f"\nMODEL: {model_type}")

        chunks, embeddings = load_data(model_type)
        index = build_index(embeddings)

        model = SentenceTransformer(
            "all-MiniLM-L6-v2" if model_type == "minilm"
            else "all-mpnet-base-v2"
        )

        results = retrieve("volcanic eruption chemistry", index, chunks, model)

        for r in results:
            print("-", r[:150])