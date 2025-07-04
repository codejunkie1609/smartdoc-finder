# SmartDoc Finder 🚀

A **self-hosted, privacy-first document search engine** with:
- ✅ Full-text search (Apache Lucene)
- ✅ Semantic search (FAISS + Sentence Embeddings)
- ✅ Hybrid Search (Combines Lucene & FAISS)
- ✅ File Upload & Indexing via Web UI

---

## 📂 Monorepo Structure (with Git Submodules)

This repo serves as the orchestration layer for the SmartDoc Finder project, linking three independent services (each as a Git submodule):

| Folder                        | Description                            |
|-------------------------------|----------------------------------------|
| `smartdoc-finder-backend`     | Spring Boot backend (Lucene + APIs)    |
| `smartdoc-finder-frontend`    | Next.js frontend (Web Interface)       |
| `smartdoc-finder-embedding`   | FastAPI embedding + semantic search API |

> 📝 Note: Each submodule points to its own Git repository.

---

## 📦 Features
- Upload & index documents (PDF, DOCX, TXT).
- Advanced full-text search with Lucene analyzers.
- Semantic search with FAISS & Sentence Transformers.
- Hybrid ranking combining both Lucene & FAISS.
- Real-time indexing progress via Server-Sent Events (SSE).
- Fully Dockerized, ready for local use or deployment.

---

## 🐳 Getting Started (Development Mode)

### 1. Clone with Submodules:
```bash
git clone --recurse-submodules https://github.com/your-org/smartdoc-finder.git
