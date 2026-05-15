# AskKMIT: Smart RAG Document Assistant 📄🧠

A powerful, rate-limit-safe intelligent document chatbot built with **Streamlit**, **LangChain**, and **Google Gemini 2.5**. This application enables you to upload documents (PDF, TXT, DOCX) and ask questions through an intuitive chat interface.

Unlike standard RAG, AskKMIT features advanced query routing allowing you to query semantic context, specific **page ranges**, and even specific **chapters**.

## 🌟 Features

- **Multi-Format Support**: Upload `.pdf`, `.txt`, and `.docx` files.
- **Smart Query Routing**:
  - **Standard Semantic RAG**: Asks general questions based on document knowledge.
  - **Page-Level Extraction**: E.g., *"Summarize page 4"* or *"What is on pages 10-12?"*
  - **Chapter-Level Extraction**: E.g., *"Explain the Introduction chapter."*
- **Rate-Limit Safe**: Built-in exponential backoff and retry logic specifically designed for Google Gemini API rate limits.
- **Efficient Caching**: Vector embeddings and file fingerprints are cached locally to avoid redundant API calls and save costs when asking multiple questions or reloading unchanged documents.
- **Source Transparency**: Every AI-generated answer includes the exact references, page numbers, and source document chunks used to generate it.

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Framework**: [LangChain](https://www.langchain.com/)
- **LLM**: Google Gemini `gemini-2.5-flash`
- **Embeddings**: Google Generative AI `gemini-embedding-001`
- **Vector Database**: FAISS (Local CPU)

## 🚀 Getting Started

### Prerequisites

You need Python 3.8+ installed on your system, along with a Google Gemini API Key. You can get a free API key from Google AI Studio.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Priyanshu-Yadav19/DocuMind-AI-Smart-RAG-Document-Assistant.git AskKMIT
   cd AskKMIT
   ```

2. **Install dependencies:**
   It is highly recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Google API Key:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Running the App

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

## 📁 Project Structure

```text
├── app.py                  # Main Streamlit application UI and routing
├── requirements.txt        # Project Python dependencies
├── .env                    # Secret environment variables (ignored in Git)
├── .gitignore              # Files to ignore in version control
└── src/                    # Core logic modules
    ├── config.py           # Configuration parameters and retry/wait constants
    ├── document_processor.py # PDF/TXT/DOCX loaders and text chunking logic
    ├── llm_service.py      # Gemini configuration, prompts, and retry/rate-limit logic
    ├── query_parser.py     # Regex and parsing logic for page/chapter queries
    ├── utils.py            # Helper utilities and file validation functions
    └── vector_store.py     # FAISS vector store creation, caching, and loading
```

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests with improvements.
