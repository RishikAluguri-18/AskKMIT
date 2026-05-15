import os
import time
from typing import List

import streamlit as st
from langchain_community.vectorstores import FAISS

from src.config import EMBED_BATCH_SIZE, SLEEP_BETWEEN_EMBED_BATCHES, MAX_RETRIES, MAX_TOTAL_CHUNKS
from src.utils import is_rate_limit, backoff_sleep, cache_dir
from src.llm_service import embeddings_model
from src.document_processor import load_documents, split_docs


# ===================== EMBEDDINGS + VECTORSTORE =====================
def embed_with_retry(texts: List[str]):
    vectors = []
    total = len(texts)
    for i in range(0, total, EMBED_BATCH_SIZE):
        batch = texts[i : i + EMBED_BATCH_SIZE]
        for attempt in range(MAX_RETRIES):
            try:
                vecs = embeddings_model.embed_documents(batch)
                vectors.extend(vecs)
                break
            except Exception as e:
                if is_rate_limit(e):
                    st.warning(f"⏳ Embed rate limit hit. Retrying... (attempt {attempt+1}/{MAX_RETRIES})")
                    backoff_sleep(attempt)
                else:
                    raise
        time.sleep(SLEEP_BETWEEN_EMBED_BATCHES)
    return vectors


def load_cached(fp: str):
    index_dir = cache_dir(fp)
    if not os.path.exists(index_dir):
        return None
    try:
        return FAISS.load_local(index_dir, embeddings_model, allow_dangerous_deserialization=True)
    except Exception:
        return None


def save_cache(fp: str, vs: FAISS):
    vs.save_local(cache_dir(fp))


def build_vectorstore(files):
    docs = load_documents(files)
    chunks = split_docs(docs)

    if not chunks:
        st.error("❌ No text could be extracted from the uploaded documents. They might be empty or contain only images.")
        st.stop()

    if len(chunks) > MAX_TOTAL_CHUNKS:
        st.error(f"❌ Too many chunks ({len(chunks)}). Upload smaller docs.")
        st.stop()

    texts = [c.page_content for c in chunks]
    metas = [c.metadata for c in chunks]

    with st.spinner(f"Embedding {len(texts)} chunks..."):
        vectors = embed_with_retry(texts)

    return FAISS.from_embeddings(list(zip(texts, vectors)), embedding=embeddings_model, metadatas=metas)


# ===================== CONTEXT FORMAT =====================
def format_context(docs):
    out = []
    for d in docs:
        src = d.metadata.get("source", "Unknown")
        page = d.metadata.get("page", None)
        chap = d.metadata.get("chapter", None)

        head = f"[Source: {src}]"
        if chap is not None:
            head += f" [Chapter: {chap}]"
        if isinstance(page, int):
            head += f" [Page: {page+1}]"

        out.append(f"{head}\n{d.page_content}")
    return "\n\n".join(out)
