from fastapi import FastAPI, Query
from pydantic import BaseModel
import json
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
PDF_FOLDER = "pdf"

# Optional: Allow testing from browser tools or external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== Models ====
class QueryRequest(BaseModel):
    email: str
    question: str

# ==== Helpers ====

def get_user_files(email):
    with open("user_access.json", "r") as f:
        access = json.load(f)
    return access.get(email, [])

def load_user_docs(user_email):
    filenames = get_user_files(user_email)
    docs = []
    allowed_files = []

    for fname in filenames:
        if not fname.lower().endswith(".pdf"):
            fname += ".pdf"
        filepath = os.path.join(PDF_FOLDER, fname)
        if os.path.exists(filepath):
            loader = PyPDFLoader(filepath)
            try:
                file_docs = loader.load()
                for doc in file_docs:
                    doc.metadata["source_file"] = fname
                docs.extend(file_docs)
                allowed_files.append(fname)
            except Exception as e:
                print(f"[Error] Failed to load {fname}: {e}")
        else:
            print(f"[Warning] File not found: {filepath}")

    print(f"[DEBUG] Loaded files for {user_email}: {allowed_files}")
    return docs

def build_vectorstore(documents):
    embeddings = OllamaEmbeddings(model="phi3:mini")
    return FAISS.from_documents(documents, embeddings)

def run_qa(user_email, query):
    documents = load_user_docs(user_email)
    if not documents:
        return {"answer": "You have no access to any valid documents.", "sources": []}

    db = build_vectorstore(documents)
    retriever = db.as_retriever()
    relevant_docs = retriever.get_relevant_documents(query)

    if not relevant_docs:
        return {"answer": "Sorry, no relevant content found in your allowed files.", "sources": []}

    llm = Ollama(model="phi3:mini")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    result = qa({"query": query})
    answer = result["result"]

    sources = []
    for doc in result["source_documents"]:
        file = doc.metadata.get("source_file", "Unknown")
        page = doc.metadata.get("page", "Unknown")
        sources.append(f"{file}, page {page}")

    return {"answer": answer, "sources": sources}

# ==== FastAPI Endpoint ====

@app.post("/query")
def ask_query(req: QueryRequest):
    response = run_qa(req.email, req.question)
    return response
