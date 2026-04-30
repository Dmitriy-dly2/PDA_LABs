import requests
import re
import xml.etree.ElementTree as ET
import pandas as pd
import pickle
import os
import time
from sentence_transformers import SentenceTransformer


QUERY = "cat:cs.LG"
MAX_RESULTS = 300


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
                    authors = [
                        author.find("atom:name", ns).text
                        for author in entry.findall("atom:author", ns)
                    ]

                    data.append({
                        "title": entry.find("atom:title", ns).text,
                        "authors": ", ".join(authors),
                        "summary": entry.find("atom:summary", ns).text
                    })

                return pd.DataFrame(data)

            except Exception as e:
                print("Retry:", e)
                time.sleep(2)

    raise Exception("Failed to fetch arXiv data")


def chunk_text(text, chunk_size=500, overlap=50):
    # Очистка текста и разделение на слова
    words = re.findall(r'\w+', text)

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        # сдвиг окна
        start += (chunk_size - overlap)

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

    print("\n=== SAMPLE CHUNK TEST ===")

    sample_summary = df.iloc[0]["summary"]
    sample_chunks = chunk_text(sample_summary)

    print("Number of chunks in first article:", len(sample_chunks))
    print("First chunk:\n", sample_chunks[0])

    num_articles = len(df)
    total_chunks = len(chunks)
    avg_chunks = total_chunks / num_articles if num_articles > 0 else 0

    print("\n=== STATISTICS ===")
    print("Number of articles:", num_articles)
    print("Saved chunks:", total_chunks)
    print("Average chunks per article:", round(avg_chunks, 2))