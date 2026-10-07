# 🏛️ Kolhapur Tourism AI Assistant

An AI-powered tourism assistant built for **Kolhapur Tourism**. It combines rule-based responses with **RAG (Retrieval-Augmented Generation)** to answer Kolhapur-specific tourism questions using a curated knowledge base.

## 🚀 Features

- 🤖 RAG-based tourism Q&A
- 📚 Kolhapur tourism PDF knowledge base
- 🔎 FAISS similarity search
- 🧠 Sentence Transformers embeddings
- ⚡ Groq-powered LLM responses
- 🔐 User authentication with MongoDB
- 💬 FastAPI web chat interface
- ⚡ Rule-based instant responses for simple messages

## 🏗️ Architecture

```text
User
 ↓
Web Chat UI
 ↓
FastAPI
 ↓
Query Routing
 ├── Simple Query → Instant Response
 ├── Kolhapur Query → RAG
 │                    ↓
 │                 Embeddings
 │                    ↓
 │                 FAISS
 │                    ↓
 │              Relevant Context
 │                    ↓
 │                 Groq LLM
 └── General Travel → Groq LLM
```

## 🛠️ Tech Stack

- Python
- FastAPI
- MongoDB
- FAISS
- Sentence Transformers
- Groq API
- Llama 3.1 8B Instant
- HTML / CSS / JavaScript

## 📁 Project Structure

```text
app/
├── main.py
├── auth.py
├── chatbot.py
├── database.py
├── rag.py
└── utils.py

knowledge_base/
└── travel.pdf

faiss_index/
├── index.faiss
├── index.pkl
└── metadata.json

static/
templates/
requirements.txt
```

## 🔥 RAG Flow

```text
Tourism PDF
    ↓
Text Cleaning & Chunking
    ↓
MiniLM Embeddings
    ↓
FAISS Index
    ↓
User Question
    ↓
Similarity Search
    ↓
Relevant Context
    ↓
Groq LLM
    ↓
Grounded Answer
```

## 🔐 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
```

The `.env` file is excluded from GitHub.

## 🎯 Project Goal

To provide a simple, fast and grounded AI assistant that helps users explore **Kolhapur's tourism information** through natural-language conversations.