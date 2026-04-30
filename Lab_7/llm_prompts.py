import pickle
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
        max_new_tokens=200,
        do_sample=False,
        num_beams=4,
        repetition_penalty=1.2
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

PROMPTS = [
    # 1
    "Summarize the main machine learning contributions in 4-5 sentences:\n{context}",

    # 2
    "Describe the key contributions of the machine learning model or method in detail:\n{context}",

    # 3
    "Explain the learning objective, loss function, or optimization process described in the text:\n{context}",

    # 4
    "Describe the model architecture, training procedure, and dataset used in the study:\n{context}",

    # 5
    "List the experimental results, improvements, and conclusions of the paper:\n{context}"
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
    retrieved = retrieve(query, index, chunks, emb_model, k=5)
    context = "\n\n---\n\n".join(retrieved[:2])

    prompt = f"""
    You are a strict scientific assistant.

    Task: answer ONLY using the context.

    If information is missing, say "Not specified in context".

    Context:
    {context}

    Question:
    {query}

    Answer in structured form:
    - Main idea
    - Method
    - Results
    - Conclusion
    """

    return ask(prompt), context


if __name__ == "__main__":
    query = "How are neural networks applied in machine learning for anomaly detection and intrusion detection tasks?"

    for model_type in ["minilm", "mpnet"]:
        print(f"\n=== RAG ({model_type}) ===")
        answer, context = rag_answer(query, model_type)
        print(answer)

    print("\n=== PROMPT TEST ===")
    answer, context = rag_answer(query)

    for i, p in enumerate(PROMPTS):
        print(f"\nPROMPT {i+1}")
        print(ask(p.format(context=context)))

    # БЕЗ RAG
    print("\n=== NO RAG ===")
    print(ask(f"Explain in detail (4-5 sentences): {query}"))