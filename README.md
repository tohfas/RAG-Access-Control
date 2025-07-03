# RAG-RBAC Demo 

(LangChain + Ollama + FAISS + FastAPI)

This project is a demo of a Retrieval-Augmented Generation (RAG) application with Role-Based Access Control (RBAC). It uses LangChain, Ollama, FAISS, and FastAPI to ensure users can only access the document data they're authorized for.


## Features

- RAG-powered Q&A using LangChain
- FAISS vector store for local document retrieval
- User/Role-based access to documents
- FastAPI backend

## For Client Testing 

Best approach - Please Note to inform me a day before testing about date and time so that I can make things moving for best result since Ollama runs and spins locally currently.

## Setup Instructions

### 1. Clone the Repository

Choose an IDE like VS Code

bash
git clone https://github.com/<your-username>/rag_rbac_demo.git
cd rag_rbac_demo

# Prerequisites & Setup Guide for Running Ollama with LangChain + FAISS (If testing on own - better approach is shown above)

This guide walks you through installing all the necessary tools to run a Retrieval-Augmented Generation (RAG) system with role-based access control (RBAC), powered by Ollama and LangChain.

Before starting, ensure you have the following installed:

- **Python** 3.9 or later  
- **pip** package manager (comes with Python)


## Install Required Python Libraries

### Install LangChain

```bash
pip install langchain langchain-community langchain-core
```

### Install FAISS (for vector search)

```bash
pip install faiss-cpu
```

---

## Install Ollama (to run local LLMs like `phi3:mini`)

### 1. Download and Install Ollama

Visit the official website:  
https://ollama.com/download

Choose your operating system and install:

- **Windows** → `.exe` installer  
- **macOS** → `.dmg` installer  
- **Linux** → Shell script or Docker  

Follow the setup wizard to complete the installation.


### 2. Verify Installation

After installation, open your terminal and run:

```bash
ollama --version
```

Expected output:

```bash
ollama version 0.x.x
```

---

### 3. Pull a Model (e.g., `phi3:mini`)

To download the `phi3:mini` model, run:

```bash
ollama pull phi3:mini
```

Browse all available models:  
https://ollama.com/library


### 4. Run the Model

Once the model is installed, start a local chat session:

```bash
ollama run phi3:mini
```

You’ll now see a local LLM interface where you can chat with the model.

You're now ready to integrate Ollama with LangChain and FAISS!

## Run the FastAPI App

Assuming your FastAPI app file is named `app.py`:
```bash
uvicorn app:app --reload
```

Access your app at `http://127.0.0.1:8000`


## Set Up Ngrok

### Step 1: Install Ngrok

#### Option 1: Chocolatey (Windows)
```bash
choco install ngrok
```

#### Option 2: Manual Download
Go to [https://ngrok.com/download](https://ngrok.com/download), download & unzip.

### Step 2: Authenticate Ngrok - You can find  YOUR_AUTH_TOKEN in your ngrok website API
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 3: Start Tunnel
```bash
ngrok http 8000
```

You’ll get a public URL like:
```
https://abcd-1234.ngrok-free.app/docs#/default/ask_query_query_post
```

### Use this URL in Copilot Studio 

Go to Copilot Studio -> Agent -> Poly -> Overview -> Topics -> See all -> System -> Conversation Poly -> URL (paste the url here) -> Headers and Body (Click Edit) -> Body (Go to Edit JSON, change email to your email, eg: test1@clearai.com.au) -> Open IDE where your git clone is -> Go to user_access.json -> Change/Add license in the same format for your email id if not present in the same format as others -> Start conversation in Copilot Studio Agent (Poly).


## Setup Instructions

### 1. Clone the Repository

bash
git clone https://github.com/<your-username>/rag_rbac_demo.git
cd rag_rbac_demo
