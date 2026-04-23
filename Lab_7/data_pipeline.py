import requests
import xml.etree.ElementTree as ET
import pandas as pd
import pickle
import os
import time
from sentence_transformers import SentenceTransformer


QUERY = "all:volcanology"
MAX_RESULTS = 100


def fetch_arxiv_data(query, max_results):
    urls = [
        "https://export.arxiv.org/api/query?"
    ]

    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"search_query": query, "max_results": max_results}

    for url in urls:
        for attempt in range(3):
            try:
                print(f"Trying {url} attempt {attempt+1}")
                r = requests.get(url, params=params, headers=headers, timeout=10)

                if r.status_code != 200:
                    continue

                if not r.text.strip().startswith("<?xml"):
                    continue

                root = ET.fromstring(r.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}

                data = []
                for entry in root.findall("atom:entry", ns):
                    data.append({
                        "title": entry.find("atom:title", ns).text,
                        "summary": entry.find("atom:summary", ns).text
                    })

                return pd.DataFrame(data)

            except Exception as e:
                print("Retry:", e)
                time.sleep(2)

    raise Exception("Failed to fetch arXiv data")


def chunk_text(text, size=300, overlap=30):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i+size]))
        i += size - overlap
    return chunks


if __name__ == "__main__":
    print("Loading arXiv...")
    df = fetch_arxiv_data(QUERY, MAX_RESULTS)

    print("Chunking...")
    chunks = []
    for s in df["summary"]:
        chunks.extend(chunk_text(s))

    print("Embedding (2 models)...")

    model1 = SentenceTransformer("all-MiniLM-L6-v2")
    model2 = SentenceTransformer("all-mpnet-base-v2")

    emb1 = model1.encode(chunks)
    emb2 = model2.encode(chunks)

    os.makedirs("models", exist_ok=True)

    with open("models/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    with open("models/embeddings_minilm.pkl", "wb") as f:
        pickle.dump(emb1, f)

    with open("models/embeddings_mpnet.pkl", "wb") as f:
        pickle.dump(emb2, f)

    print(f"Saved {len(chunks)} chunks")