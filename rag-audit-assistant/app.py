"""
RAG Audit Assistant
-------------------
A command-line RAG system for querying ASAE 3402 audit guidance.

Built with: LangChain, ChromaDB, OpenAI
Author: Marcus Tiong
"""

import os
import sys
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


# ── Configuration ──────────────────────────────────────────────────────────────

DATA_PATH = "data/asae3402_guidance.txt"
CHROMA_DB_PATH = "./chroma_db"
OPENAI_MODEL = "gpt-3.5-turbo"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K_RESULTS = 4


# ── Prompt template ────────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """You are an expert audit assistant specialising in ASAE 3402 
and IT General Controls. Use the following context from the ASAE 3402 guidance 
document to answer the question accurately and concisely.

If the answer is not contained in the context, say: 
"I don't have enough information in the loaded documents to answer that. 
Try rephrasing or ask about a different aspect of ASAE 3402."

Always be precise and use correct audit terminology.

Context:
{context}

Question: {question}

Answer:"""


# ── Core functions ─────────────────────────────────────────────────────────────

def check_api_key():
    """Check that an OpenAI API key is set."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌  OPENAI_API_KEY environment variable not set.")
        print("    Set it by running: export OPENAI_API_KEY='your-key-here'")
        print("    Get a key at: https://platform.openai.com/api-keys\n")
        sys.exit(1)
    return api_key


def load_and_split_documents(path: str):
    """Load the guidance document and split it into chunks."""
    print(f"📄  Loading document: {path}")
    loader = TextLoader(path, encoding="utf-8")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️   Split into {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


def build_or_load_vectorstore(chunks, embeddings):
    """Build a ChromaDB vector store from chunks, or load existing one."""
    if os.path.exists(CHROMA_DB_PATH) and os.listdir(CHROMA_DB_PATH):
        print("🗄️   Loading existing vector store from disk...")
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings
        )
    else:
        print("🔨  Building vector store (this may take a moment)...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DB_PATH
        )
        print("💾  Vector store saved to disk.")
    return vectorstore


def build_qa_chain(vectorstore):
    """Build the RetrievalQA chain with a custom prompt."""
    llm = ChatOpenAI(model_name=OPENAI_MODEL, temperature=0)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K_RESULTS}
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return qa_chain


def print_answer(result: dict):
    """Print the answer and source chunks used."""
    print("\n" + "─" * 60)
    print("💬  Answer:\n")
    print(result["result"])
    print("\n" + "─" * 60)
    print(f"📚  Based on {len(result['source_documents'])} retrieved chunk(s).")
    print("─" * 60 + "\n")


# ── Main loop ──────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  RAG AUDIT ASSISTANT — ASAE 3402 Guidance")
    print("=" * 60)

    # 1. Check API key
    check_api_key()

    # 2. Load and chunk documents
    chunks = load_and_split_documents(DATA_PATH)

    # 3. Build embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = build_or_load_vectorstore(chunks, embeddings)

    # 4. Build QA chain
    print("⚙️   Initialising QA chain...")
    qa_chain = build_qa_chain(vectorstore)

    print("\n✅  Ready! Ask questions about ASAE 3402.")
    print("    Type 'quit' or 'exit' to stop.\n")

    # 5. Question loop
    while True:
        try:
            question = input("🔍  Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit"):
            print("\nGoodbye!")
            break

        print("\n⏳  Retrieving and generating answer...")
        result = qa_chain.invoke({"query": question})
        print_answer(result)


if __name__ == "__main__":
    main()
