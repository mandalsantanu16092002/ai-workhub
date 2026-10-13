::: {align="center"}
# AI WorkHub

### Intelligent Document & Knowledge Assistant

A full-stack knowledge-management platform in development, designed to
make document collections easier to organize, search, and query using
retrieval-augmented generation (RAG).

**Next.js · TypeScript · FastAPI · PostgreSQL · pgvector**

[Overview](#overview) · [Features](#implemented-and-planned) ·
[Architecture](#architecture) · [Setup](#getting-started) ·
[API](#api-reference) · [Roadmap](#roadmap)
:::

------------------------------------------------------------------------

> **Project status: In active development**
>
> The current release establishes the application foundation: a FastAPI
> backend, PostgreSQL persistence, versioned database migrations,
> document-metadata CRUD endpoints, structured error responses, initial
> automated tests, and a Next.js frontend scaffold. Actual file
> ingestion, embeddings, semantic retrieval, RAG, and end-to-end
> frontend integration are planned work.

## Overview

AI WorkHub is being built around a practical workflow for working with a
personal or team document collection:

1.  Add documents to a workspace.
2.  Extract and normalize document text.
3.  Split text into searchable chunks.
4.  Generate vector embeddings.
5.  Retrieve relevant passages through semantic search.
6.  Ask questions and receive answers grounded in retrieved source
    material.

The repository currently contains the backend and database foundation
for this workflow. The end-to-end AI workflow is not yet implemented.

## Implemented and planned

### Implemented

-   **FastAPI application** with a health endpoint and interactive API
    documentation.
-   **PostgreSQL persistence** using SQLAlchemy.
-   **Versioned schema migrations** managed by Alembic.
-   **Document metadata endpoints** to create, list, retrieve, and
    delete records.
-   **Request validation** using Pydantic schemas.
-   **Structured error handling** for application errors, validation
    failures, and unexpected exceptions.
-   **Relational integrity** with foreign keys, constraints, and
    cascading deletion of document chunks.
-   **Initial automated tests** for health checks and document API
    behavior.
-   **Frontend scaffold** using Next.js, TypeScript, and Tailwind CSS.

### Planned

-   Real document upload and file storage.
-   File-type and size validation.
-   Text extraction, normalization, and chunking.
-   Embedding generation and persistence.
-   Semantic retrieval using pgvector.
-   Retrieval-augmented question answering with source references.
-   Frontend-to-backend integration.
-   Containerized development and CI/CD.
-   End-to-end deployment and demonstration.

## Technology stack

  -----------------------------------------------------------------------
  Layer                   Technology              Current role
  ----------------------- ----------------------- -----------------------
  Frontend                Next.js, React,         Application scaffold
                          TypeScript, Tailwind    
                          CSS                     

  API                     Python, FastAPI,        Implemented backend API
                          Pydantic                

  Data access             SQLAlchemy              ORM and database access

  Database                PostgreSQL              Metadata persistence

  Vector capability       pgvector                Extension foundation;
                                                  embedding retrieval is
                                                  planned

  Migrations              Alembic                 Versioned schema
                                                  changes

  Testing                 pytest, FastAPI         Backend test suite
                          TestClient, HTTPX       

  Version control         Git, GitHub             Source control and
                                                  collaboration

  Infrastructure          Docker, GitHub Actions  Development tools;
                                                  automated deployment
                                                  pipeline planned
  -----------------------------------------------------------------------

## Architecture

The intended architecture separates the frontend, API, business logic,
data-access layer, and database.

``` text
┌──────────────────────────────────────┐
│            Next.js Frontend          │
│       Document Workspace / Chat      │
└───────────────────┬──────────────────┘
                    │ HTTP / JSON
                    ▼
┌──────────────────────────────────────┐
│             FastAPI API              │
│                                      │
│  Routes → Services → Repositories    │
│              │                       │
│     Pydantic Validation              │
│     Structured Error Handling        │
└───────────────────┬──────────────────┘
                    │ SQLAlchemy
                    ▼
┌──────────────────────────────────────┐
│              PostgreSQL              │
│       Documents / Document Chunks    │
│          pgvector extension          │
└──────────────────────────────────────┘
```

**Current boundary:** the diagram describes the intended product
architecture. The frontend is scaffolded, while end-to-end frontend
integration, file ingestion, embedding storage, semantic retrieval, and
question answering remain future work.

## Repository structure

``` text
ai-workhub/
├── backend/
│   ├── app/
│   │   ├── api/              # HTTP routes
│   │   ├── core/             # Configuration and error handling
│   │   ├── db/               # SQLAlchemy base and sessions
│   │   ├── models/           # Database models
│   │   ├── repositories/     # Database operations
│   │   ├── schemas/          # Request and response schemas
│   │   ├── services/         # Application logic
│   │   └── main.py           # FastAPI application
│   ├── migrations/           # Alembic migrations
│   ├── tests/                # Automated backend tests
│   ├── .env.example          # Environment-variable template
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
├── docs/
│   └── screenshots/
├── .gitignore
└── README.md
```

## Getting started

### Prerequisites

-   Python 3.11
-   Node.js and npm
-   Git
-   PostgreSQL with the pgvector extension available
-   A terminal such as Windows CMD, PowerShell, or a Unix shell

The commands below use Windows CMD where activation syntax differs.

### 1. Clone the repository

Replace the URL below with the repository's HTTPS URL.

``` bash
git clone https://github.com/mandalsantanu16092002/ai-workhub.git
cd ai-workhub
```

### 2. Configure PostgreSQL

Create a local PostgreSQL database and user, and ensure the pgvector
extension is available. The original local development setup used:

-   Database: `workhub`
-   User: `workhub`
-   Host port: `5434`

Use your own local credentials. Never reuse development credentials in a
public deployment.

### 3. Configure the backend

``` bash
cd backend
python -m venv .venv
```

Activate the environment.

**Windows CMD**

``` cmd
.venv\Scripts\activate
```

**PowerShell**

``` powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

``` bash
source .venv/bin/activate
```

Install dependencies:

``` bash
python -m pip install -r requirements.txt
```

Create `backend/.env` using `.env.example` as a template. Update
`DATABASE_URL` to match your local PostgreSQL username, password, host,
port, and database.

Example format:

``` dotenv
APP_NAME=AI WorkHub API
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000"]
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5434/workhub
```

Keep `.env` local and untracked. Do not commit real passwords, tokens,
or other secrets.

### 4. Apply database migrations

From the `backend` directory, with the virtual environment activated and
`.env` configured:

``` cmd
alembic upgrade head
```

### 5. Start the backend

``` cmd
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

The backend will be available at:

  Resource         URL
  ---------------- --------------------------------------
  API base         `http://127.0.0.1:8001`
  Health check     `http://127.0.0.1:8001/health`
  Swagger UI       `http://127.0.0.1:8001/docs`
  OpenAPI schema   `http://127.0.0.1:8001/openapi.json`

### 6. Start the frontend

Open a second terminal at the repository root:

``` cmd
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The frontend is currently a scaffold; full integration with the document
API is still in development.

## API reference

The current backend exposes these endpoints:

  --------------------------------------------------------------------------------
  Method                  Endpoint                         Purpose
  ----------------------- -------------------------------- -----------------------
  `GET`                   `/health`                        Return application
                                                           health information

  `POST`                  `/api/documents`                 Create a document
                                                           metadata record

  `GET`                   `/api/documents`                 List document metadata

  `GET`                   `/api/documents/{document_id}`   Retrieve one document
                                                           record

  `DELETE`                `/api/documents/{document_id}`   Delete a document
                                                           record
  --------------------------------------------------------------------------------

### Create a document metadata record

`POST /api/documents`

Example request:

``` json
{
  "filename": "sample.pdf",
  "content_type": "application/pdf",
  "file_size": 1024,
  "stored_path": "uploads/sample.pdf"
}
```

A successful request returns `201 Created` and the created record.

**Important limitation:** this endpoint records metadata only. It does
not upload, validate, or store the actual file. The `stored_path` value
is metadata at this stage.

### Error responses

The API uses structured error responses for expected application errors
and validation failures. Common HTTP statuses include:

-   `201 Created` --- metadata record created.
-   `204 No Content` --- record deleted successfully.
-   `404 Not Found` --- requested document does not exist.
-   `422 Unprocessable Entity` --- request validation failed.
-   `500 Internal Server Error` --- unexpected server error.

Use `/docs` for the live interactive API schema while the backend is
running.

## Database design

### `documents`

Stores metadata for each document:

-   UUID primary key.
-   Filename, content type, and file size.
-   Internal storage-path field.
-   Processing status.
-   Creation and update timestamps.

Available statuses:

-   `uploaded`
-   `processing`
-   `ready`
-   `failed`

### `document_chunks`

Stores text chunks associated with a document:

-   UUID primary key.
-   Parent document UUID.
-   Chunk index.
-   Text content.
-   Creation timestamp.

The schema enforces uniqueness for `(document_id, chunk_index)` and uses
a foreign key with `ON DELETE CASCADE`. Embedding persistence and vector
retrieval are not yet implemented.

## Testing

Run the backend tests from the `backend` directory with the virtual
environment activated:

``` cmd
python -m pytest -v
```

Tests should use a dedicated test database, separate from development
and production databases. Confirm the test configuration before running
tests that write to a database.

## Screenshots

The repository includes screenshots of the current backend development
progress.

### API overview

![API overview](docs/screenshots/api-overview.png)

### Health check

![Health check](docs/screenshots/health-check.png)

### Automated tests

![Automated tests](docs/screenshots/automated-tests.png)

## Roadmap

-   [x] Initialize frontend and backend foundations
-   [x] Configure PostgreSQL and pgvector extension support
-   [x] Add SQLAlchemy models and Alembic migrations
-   [x] Implement document metadata CRUD endpoints
-   [x] Add structured API error handling
-   [x] Add initial backend tests
-   [ ] Finalize isolated test-database configuration
-   [ ] Implement real document uploads and storage
-   [ ] Extract text and create chunks
-   [ ] Generate and persist embeddings
-   [ ] Implement semantic search
-   [ ] Add RAG question answering with source references
-   [ ] Integrate the frontend with the backend
-   [ ] Add CI/CD and deployment configuration
-   [ ] Publish an end-to-end demo

## Engineering principles

The project is being developed with an emphasis on:

-   Separation of routes, services, repositories, and database models.
-   Explicit request and response schemas.
-   Consistent error handling.
-   Version-controlled database migrations.
-   Environment-based configuration and secret hygiene.
-   Automated tests and incremental delivery.
-   Clear documentation of implemented functionality and remaining work.

## Contributing

This is an actively developed portfolio project. For now, bug reports
and focused suggestions are welcome through GitHub Issues. Before
proposing a feature, check the roadmap and existing issues to avoid
duplicating work.

## License

No license has been selected yet. Until a license is added, the
repository should be treated as **all rights reserved**; do not assume
permission to reuse, modify, or redistribute the code.
