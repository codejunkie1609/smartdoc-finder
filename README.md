SmartDoc Finder 🚀
A self-hosted, privacy-first, Retrieval-Augmented Generation (RAG) engine designed to answer questions using your own documents. This project combines advanced search techniques with large language models to provide accurate, context-aware answers.

✅ Hybrid Search: Combines keyword (Lucene) and semantic (FAISS) search for initial document retrieval.

✅ Re-ranking: Uses a sophisticated cross-encoder model to re-rank the initial results for maximum relevance.

✅ Generative Answers: Leverages a local LLM (via Ollama) to generate natural language answers based on the top-ranked documents.

✅ Event-Driven Architecture: Built on a robust microservices architecture orchestrated with RabbitMQ for asynchronous processing.

✅ Fully Containerized: The entire stack is containerized with Docker Compose for easy setup and deployment.

🏛️ Architecture Overview
The system follows a multi-stage RAG pipeline to ensure high-quality, factual answers:

Indexing Pipeline (Asynchronous):

Documents are uploaded and their text is extracted.

The backend saves the document to a PostgreSQL database.

An event is published to a RabbitMQ queue.

Two independent workers consume the event:

The embedding-worker generates vector embeddings and adds them to a FAISS index.

The backend indexes the text content in Apache Lucene.

Search & Generation Pipeline (Real-time):

Stage 1: Retrieval: A user's query is sent to the backend, which performs a hybrid search across both the Lucene and FAISS indexes to retrieve a broad set of 50 candidate documents.

Stage 2: Re-ranking: These 50 candidates are sent to the reranker service, which uses a powerful cross-encoder model to re-order them and select the top 5 most relevant documents.

Stage 3: Generation: The query and the top 5 documents are sent to the generator service, which constructs a detailed prompt and uses a local LLM (via Ollama) to generate a final answer.

📂 Monorepo Structure (with Git Submodules)
This repository serves as the orchestration layer for the project, linking several independent services (each as a Git submodule):

Folder

Description

smartdoc-finder-backend

Spring Boot backend (APIs, Lucene, Orchestration)

smartdoc-finder-frontend

Next.js frontend (Web Interface)

smartdoc-finder-embedding

FastAPI service for semantic search (FAISS) and embedding.

smartdoc-finder-reranker

FastAPI service for re-ranking search results.

smartdoc-finder-generator

FastAPI service that calls the LLM to generate answers.

smartdoc-finder-ollama

Docker configuration for the self-hosted Ollama LLM service.

📝 Note: Each submodule points to its own Git repository. To clone the project correctly, you must include the submodules.

🐳 Getting Started (Development Mode)
Prerequisites
Docker & Docker Compose

Git

An .env file in the project root (see .env.example for the required variables).

1. Clone with Submodules
Because this project uses Git submodules, you must use the --recurse-submodules flag when cloning:

git clone --recurse-submodules [https://github.com/](https://github.com/)<Your-Username>/smartdoc-finder.git
cd smartdoc-finder

2. Configure Your Environment
Create a .env file in the project root. You can copy the .env.example file to get started. The most important variable to set is USER_DATA_DIRECTORY, which should point to the folder on your local machine containing the documents you want to index.

3. Build and Run the Application
This command will build all the service images and start the containers.

docker-compose up --build

4. Download AI Models (First-Time Setup)
The first time you run the application, the AI services need to download their models. This can take several minutes. You can monitor the progress by watching the logs.

Ollama (Generator): The ollama service will automatically start downloading the model specified in its entrypoint.sh script (e.g., qwen2:0.5b).

Embedding & Reranker: These services will download their models when they first start up.

The application will be ready to use once all services are running and the models are downloaded.
