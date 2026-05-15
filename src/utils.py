import os
import time
import hashlib
import streamlit as st

from src.config import MAX_FILE_SIZE_MB, MAX_TOTAL_SIZE_MB, BASE_WAIT_SEC

def validate_files(files) -> bool:
    total = 0.0
    for f in files:
        size = len(f.getvalue()) / (1024 * 1024)
        total += size
        if size > MAX_FILE_SIZE_MB:
            st.error(f"❌ {f.name} exceeds {MAX_FILE_SIZE_MB} MB")
            return False
    if total > MAX_TOTAL_SIZE_MB:
        st.error(f"❌ Total upload exceeds {MAX_TOTAL_SIZE_MB} MB")
        return False
    return True


def fingerprint_files(files) -> str:
    h = hashlib.sha256()
    for f in files:
        data = f.getvalue()
        h.update(f.name.encode("utf-8"))
        h.update(len(data).to_bytes(8, "big"))
        h.update(hashlib.sha256(data).digest())
    return h.hexdigest()


def cache_dir(fp: str) -> str:
    os.makedirs(".cache", exist_ok=True)
    return os.path.join(".cache", f"faiss_{fp}")


def is_rate_limit(e: Exception) -> bool:
    s = str(e).lower()
    return ("429" in s) or ("quota" in s) or ("rate" in s) or ("resourceexhausted" in s)


def backoff_sleep(attempt: int, min_wait: int = 0):
    wait = BASE_WAIT_SEC * (2 ** attempt)
    wait = max(wait, min_wait)
    time.sleep(wait)
