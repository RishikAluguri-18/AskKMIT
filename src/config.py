import os
from dotenv import load_dotenv

# ===================== ENV =====================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# ===================== LIMITS / TUNING =====================
MAX_FILE_SIZE_MB = 30
MAX_TOTAL_SIZE_MB = 60

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 120
MAX_TOTAL_CHUNKS = 1500

# Embedding batching
EMBED_BATCH_SIZE = 32
SLEEP_BETWEEN_EMBED_BATCHES = 1.0

# Retry/backoff
MAX_RETRIES = 6
BASE_WAIT_SEC = 10
MIN_LLM_WAIT_SEC = 60  # Gemini often tells ~59s; use 60s

# Retriever
RETRIEVER_K = 12
