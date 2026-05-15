import time
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate

from src.utils import is_rate_limit
from src.config import MAX_RETRIES, BASE_WAIT_SEC, MIN_LLM_WAIT_SEC

# ===================== MODELS =====================
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.2)
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# ===================== PROMPT =====================
prompt = ChatPromptTemplate.from_template(
    """Answer the question using ONLY the provided context.
If the answer is not found in the context, say "I don't know."

<context>
{context}
</context>

Question: {input}
"""
)


# ===================== LLM SAFE INVOKE =====================
def llm_invoke_with_retry(llm_obj, messages):
    for attempt in range(MAX_RETRIES):
        try:
            return llm_obj.invoke(messages).content
        except Exception as e:
            if is_rate_limit(e):
                wait = max(MIN_LLM_WAIT_SEC, BASE_WAIT_SEC * (2 ** attempt))
                st.warning(f"⏳ LLM rate limit hit. Waiting {wait}s then retrying...")
                time.sleep(wait)
            else:
                raise
    st.error("LLM rate limit keeps happening. Try again in 1–2 minutes.")
    st.stop()
