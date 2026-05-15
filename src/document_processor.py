import os
import re
import tempfile
from typing import Optional, List

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def detect_chapter_number(text: str) -> Optional[int]:
    if not text:
        return None
    m = re.search(r"\bchapter\s+(\d+)\b", text.lower())
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def load_documents(files):
    docs = []
    tmp_paths = []

    try:
        for f in files:
            ext = f.name.split(".")[-1].lower()
            data = f.getvalue()

            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                tmp.write(data)
                tmp_paths.append(tmp.name)
                path = tmp.name

            if ext == "pdf":
                loader = PyPDFLoader(path)
            elif ext == "txt":
                loader = TextLoader(path, encoding="utf-8")
            elif ext == "docx":
                loader = Docx2txtLoader(path)
            else:
                continue

            loaded = loader.load()
            for d in loaded:
                d.metadata["source"] = f.name
                d.metadata["ext"] = ext
                chap = detect_chapter_number(d.page_content[:4000])
                if chap is not None:
                    d.metadata["chapter"] = chap

            docs.extend(loaded)
    finally:
        for p in tmp_paths:
            try:
                os.remove(p)
            except OSError:
                pass

    return docs


def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(docs)

# ===================== SELECTION LOGIC =====================
def select_pdf_pages(all_docs, mode):
    pdf_docs = [d for d in all_docs if d.metadata.get("ext") == "pdf" and "page" in d.metadata]
    if not pdf_docs:
        return []

    sources = sorted(set(d.metadata.get("source", "Unknown") for d in pdf_docs))
    src0 = sources[0]
    pages = sorted([d for d in pdf_docs if d.metadata.get("source") == src0], key=lambda x: x.metadata.get("page", 0))

    if mode[0] == "last":
        n = mode[1]
        return pages[-n:] if n > 0 else []
    if mode[0] == "range":
        a, b = mode[1], mode[2]
        start = max(a - 1, 0)
        end = max(b - 1, 0)
        return pages[start : end + 1]
    return []


def select_sections_non_pdf(all_docs, mode):
    non_pdf = [d for d in all_docs if d.metadata.get("ext") in ("txt", "docx")]
    if not non_pdf:
        return []

    sources = sorted(set(d.metadata.get("source", "Unknown") for d in non_pdf))
    src0 = sources[0]
    src_docs = [d for d in non_pdf if d.metadata.get("source") == src0]

    chunks = split_docs(src_docs)
    if not chunks:
        return []

    if mode[0] == "last":
        n = mode[1]
        return chunks[-n:] if n > 0 else []
    if mode[0] == "range":
        a, b = mode[1], mode[2]
        start = max(a - 1, 0)
        end = max(b - 1, 0)
        return chunks[start : end + 1]
    return []


def select_chapters(all_docs, chapters: List[int]):
    return [d for d in all_docs if d.metadata.get("chapter") in set(chapters)]
