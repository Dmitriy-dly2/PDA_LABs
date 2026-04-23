import pickle
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
from vector_rag import build_index, retrieve


print("Loading FLAN-T5...")

tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")


def ask(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        do_sample=True,
        temperature=0.7
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


PROMPTS = [
    "Summarize the main findings:\n{context}",
    "What are the key contributions?\n{context}",
    "Explain the causes described:\n{context}",
    "What methods are used?\n{context}",
    "List the conclusions:\n{context}"
]


def load_data(model_type="minilm"):
    with open("models/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    with open(f"models/embeddings_{model_type}.pkl", "rb") as f:
        embeddings = pickle.load(f)

    return chunks, embeddings


def rag_answer(query, model_type="minilm"):
    chunks, embeddings = load_data(model_type)

    emb_model = SentenceTransformer(
        "all-MiniLM-L6-v2" if model_type == "minilm"
        else "all-mpnet-base-v2"
    )

    index = build_index(embeddings)

    retrieved = retrieve(query, index, chunks, emb_model)

    context = "\n\n".join(retrieved[:2])  # ограничение

    prompt = f"""
You are a scientific assistant.

Using ONLY the context:
- Explain clearly
- Give key points

Context:
{context}

Question:
{query}

Answer:
"""

    return ask(prompt), context


if __name__ == "__main__":
    query = "What causes volcanic eruptions?"

    for model_type in ["minilm", "mpnet"]:
        print(f"\n=== RAG ({model_type}) ===")
        answer, context = rag_answer(query, model_type)
        print(answer)

    print("\n=== PROMPT TEST ===")
    answer, context = rag_answer(query)

    for i, p in enumerate(PROMPTS):
        print(f"\nPROMPT {i+1}")
        print(ask(p.format(context=context)))

    print("\n=== NO RAG ===")
    print(ask(f"Explain: {query}"))