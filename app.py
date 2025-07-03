from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
PDF_FOLDER = "pdf"

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    email: str
    question: str

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
            try:
                loader = PyPDFLoader(filepath)
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
    embeddings = OllamaEmbeddings(model="phi3:mini")  # Consider 'mistral' for speed
    return FAISS.from_documents(documents, embeddings)

def run_qa(user_email, query):
    documents = load_user_docs(user_email)
    if not documents:
        return {"answer": "You have no access to any valid documents."}

    db = build_vectorstore(documents)
    retriever = db.as_retriever(search_kwargs={"k": 4})
    relevant_docs = retriever.get_relevant_documents(query)

    if not relevant_docs:
        return {"answer": "Sorry, no relevant content found in your allowed files."}

    llm = Ollama(model="phi3:mini", temperature=0.1)

    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an assistant that answers questions based only on the provided context from files of Standards Australia. If you have answer and access to the relevant file, give response accurately and precisely by giving Standards, numbers and more accurate guidelines.
If the context does not contain the answer, say "I don't know." Do not make up answers STRICTLY.

Context: {context}

Question: {question}
Answer:
"""
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )

    result = qa({"query": query})
    answer = result.get("result", "").strip().lower()

    # Handle ambiguous or generic replies
    trigger_phrases = [
        "i don't know",
        "the provided document does not contain specific information",
        "no relevant information",
        "not found in the document"
    ]

    if not result["source_documents"] or any(phrase in answer for phrase in trigger_phrases):
        return {"answer": "Sorry, no relevant content found in your allowed files."}

    # Compile sources
    sources = []
    for doc in result["source_documents"]:
        file = doc.metadata.get("source_file", "Unknown")
        page = doc.metadata.get("page", "Unknown")
        sources.append(f"{file}, page {page}")

    return {"answer": result["result"].strip(), "sources": sources}

@app.post("/query")
def ask_query(req: QueryRequest):
    return run_qa(req.email, req.question)
