# RAG Audit Assistant — ASAE 3402

A command-line RAG (Retrieval-Augmented Generation) system that lets you ask plain-English questions over ASAE 3402 audit guidance documents and get precise, grounded answers.

Built as a portfolio project to demonstrate practical AI agent development skills applied to an audit and assurance context.

---

## What it does

- Loads and chunks an ASAE 3402 guidance document
- Embeds the chunks into a local ChromaDB vector store
- Accepts natural language questions via the command line
- Retrieves the most relevant document sections and generates a grounded answer using GPT-3.5
- Refuses to hallucinate — if the answer isn't in the document, it says so

### Example questions you can ask

```
What is the difference between a Type 1 and Type 2 report?
What are Complementary User Entity Controls and why do they matter?
What testing approaches can a service auditor use?
When should a service auditor issue a qualified opinion?
What are the key control objectives for access management?
How should a service organisation handle subservice organisations?
```

---

## Tech stack

| Component | Tool |
|---|---|
| Framework | LangChain |
| Vector store | ChromaDB (local) |
| Embeddings | OpenAI `text-embedding-ada-002` |
| LLM | OpenAI `gpt-3.5-turbo` |
| Language | Python 3.10+ |

---

## Project structure

```
rag-audit-assistant/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── data/
│   └── asae3402_guidance.txt # Source document
└── README.md
```

---

## Getting started

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rag-audit-assistant.git
   cd rag-audit-assistant
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Mac/Linux
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your OpenAI API key**
   ```bash
   export OPENAI_API_KEY="your-key-here"   # Mac/Linux
   set OPENAI_API_KEY=your-key-here        # Windows
   ```

5. **Run the app**
   ```bash
   python app.py
   ```

On first run, the app will build the vector store and save it to `./chroma_db/`. Subsequent runs will load it from disk — much faster.

---

## How it works

```
Your question
     │
     ▼
Embed question → Search ChromaDB for top 4 relevant chunks
     │
     ▼
Inject chunks + question into prompt → GPT-3.5 generates answer
     │
     ▼
Grounded answer printed to terminal
```

This pattern — **Retrieval-Augmented Generation** — ensures the model only answers from the actual document content, dramatically reducing hallucinations. This is especially important in audit and compliance contexts where precision and accuracy are critical.

---

## Extending this project

Some ideas for taking this further:

- **Add more documents** — drop additional `.txt` or `.pdf` files into `/data` and update the loader to ingest multiple files
- **Swap the LLM** — replace OpenAI with a local model via Ollama for a fully offline version
- **Add a web UI** — wrap `app.py` with Streamlit for a browser-based interface
- **Expand to other standards** — add SOx, ASAE 3150, or GS007 guidance documents to cover a broader compliance knowledge base

---

## About

Built by Marcus Tiong — a technology risk professional transitioning into AI implementation and governance. Background in IT audit, controls assurance, and AI agent development at PwC Australia.

[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) · [GitHub](https://github.com/YOUR_USERNAME)
