import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from src.config import GOOGLE_API_KEY, RETRIEVER_K
from src.utils import validate_files, fingerprint_files
from src.document_processor import load_documents, select_pdf_pages, select_sections_non_pdf, select_chapters
from src.vector_store import build_vectorstore, load_cached, save_cache, format_context
from src.query_parser import parse_page_request, parse_chapter_request
from src.llm_service import llm, prompt, llm_invoke_with_retry

# ===================== UI =====================
st.set_page_config(page_title="AskKMIT Chatbot", layout="wide")
st.title("📄 AskKMIT: Smart RAG Document Assistant")
st.caption("PDF/TXT/DOCX • Semantic RAG + page/section ranges + chapter selection • Cached • Rate-limit safe")

# ===================== SESSION =====================
if "vectors" not in st.session_state:
    st.session_state.vectors = None
if "fingerprint" not in st.session_state:
    st.session_state.fingerprint = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_run_key" not in st.session_state:
    st.session_state.last_run_key = None
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "last_sources" not in st.session_state:
    st.session_state.last_sources = None

# ===================== UPLOAD =====================
uploaded_files = st.file_uploader(
    "Upload PDF / TXT / DOCX files",
    type=["pdf", "txt", "docx"],
    accept_multiple_files=True,
)

# ===================== QUESTION =====================
with st.form("qa"):
    question = st.text_input("Ask a question from your documents")
    ask = st.form_submit_button("Ask")

# ===================== RUN =====================
if ask and question:
    if not GOOGLE_API_KEY:
        st.error("❌ Missing GOOGLE_API_KEY in .env")
        st.stop()

    if not uploaded_files:
        st.warning("⚠️ Upload documents first")
        st.stop()

    if not validate_files(uploaded_files):
        st.stop()

    fp = fingerprint_files(uploaded_files)

    # Prevent accidental repeated LLM calls from Streamlit re-runs
    run_key = f"{fp}::{question.strip().lower()}"
    if st.session_state.last_run_key == run_key and st.session_state.last_answer is not None:
        st.info("✅ Same question already answered (avoiding extra API calls).")
        st.subheader("Answer")
        st.write(st.session_state.last_answer)
        with st.expander("🔍 Sources / Retrieved Chunks"):
            if st.session_state.last_sources:
                for d in st.session_state.last_sources:
                    src = d.metadata.get("source", "Unknown")
                    page = d.metadata.get("page", None)
                    chap = d.metadata.get("chapter", None)
                    label = f"**{src}**"
                    if chap is not None:
                        label += f" — Chapter {chap}"
                    if isinstance(page, int):
                        label += f" — Page {page+1}"
                    st.markdown(label)
                    st.write(d.page_content)
                    st.divider()
        st.stop()

    # Build/load vectorstore for semantic RAG
    if st.session_state.vectors is None or st.session_state.fingerprint != fp:
        cached = load_cached(fp)
        if cached:
            st.session_state.vectors = cached
            st.session_state.fingerprint = fp
            st.success("✅ Loaded cached embeddings")
        else:
            vs = build_vectorstore(uploaded_files)
            save_cache(fp, vs)
            st.session_state.vectors = vs
            st.session_state.fingerprint = fp
            st.success("✅ Embeddings created & cached")

    retriever = st.session_state.vectors.as_retriever(search_kwargs={"k": RETRIEVER_K})

    t0 = time.time()

    # -------- Decide routing (chapter > page > RAG) --------
    chapter_req = parse_chapter_request(question)
    page_req = parse_page_request(question)

    if chapter_req:
        all_docs = load_documents(uploaded_files)
        docs = select_chapters(all_docs, chapter_req)
        if not docs:
            st.warning("Couldn't match chapter headings. Try 'summarize pages X-Y' instead.")
    elif page_req:
        all_docs = load_documents(uploaded_files)
        docs = select_pdf_pages(all_docs, page_req)
        if not docs:
            docs = select_sections_non_pdf(all_docs, page_req)
        if not docs:
            st.warning("Couldn't select pages/sections (PDF might be scanned).")
    else:
        docs = retriever.invoke(question)

    context = format_context(docs)
    messages = prompt.format_messages(context=context, input=question)

    answer = llm_invoke_with_retry(llm, messages)

    st.session_state.chat_history.append(HumanMessage(content=question))
    st.session_state.chat_history.append(AIMessage(content=answer))

    # Cache last run to avoid accidental repeated calls
    st.session_state.last_run_key = run_key
    st.session_state.last_answer = answer
    st.session_state.last_sources = docs

    st.subheader("Answer")
    st.write(answer)
    st.caption(f"⏱ {round(time.time() - t0, 2)} seconds")

    with st.expander("🔍 Sources / Retrieved Chunks"):
        if not docs:
            st.write("No context documents were selected/retrieved.")
        else:
            for d in docs:
                src = d.metadata.get("source", "Unknown")
                page = d.metadata.get("page", None)
                chap = d.metadata.get("chapter", None)

                label = f"**{src}**"
                if chap is not None:
                    label += f" — Chapter {chap}"
                if isinstance(page, int):
                    label += f" — Page {page+1}"

                st.markdown(label)
                st.write(d.page_content)
                st.divider()
