# Bulk SEO Content Analyzer — Project Structure & Module Reference

---

## Table of Contents

1. [Repository Root Layout](#repository-root-layout)
2. [Backend — Full File Tree](#backend--full-file-tree)
3. [Frontend — Full File Tree](#frontend--full-file-tree)
4. [Backend Module Reference](#backend-module-reference)
5. [Frontend Module Reference](#frontend-module-reference)
6. [Configuration & Infrastructure Files](#configuration--infrastructure-files)
7. [Test Suite Reference](#test-suite-reference)

---

## Repository Root Layout

```
seo-analyzer/
├── backend/
├── frontend/
├── storage/
│   └── uploads/                  # Shared bind mount — API writes, worker reads
├── docker-compose.yml
├── .env.example
└── README.md
```

The repository is a monorepo with a hard split between `backend/` and `frontend/`. The `storage/uploads/` directory lives at the root so that both the `api` Docker container and the `worker` Docker container can mount the same host path as a shared bind mount. Neither container has its own isolated copy of uploaded files — they share one directory via Docker volume binding.

---

## Backend — Full File Tree

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app factory, router registration, CORS
│   ├── config.py                      # Pydantic Settings — all env vars in one place
│   ├── database.py                    # Async SQLAlchemy engine, session factory, Base
│   │
│   ├── models/                        # SQLAlchemy ORM table definitions
│   │   ├── __init__.py
│   │   ├── user.py                    # users table
│   │   ├── document.py                # documents table
│   │   ├── processing_job.py          # processing_jobs table
│   │   └── extracted_result.py        # extracted_results table
│   │
│   ├── schemas/                       # Pydantic v2 request/response DTOs
│   │   ├── __init__.py
│   │   ├── auth.py                    # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── document.py                # DocumentResponse, DocumentListResponse
│   │   ├── job.py                     # JobResponse, JobStatusResponse
│   │   ├── result.py                  # ExtractedResultResponse, PatchResultRequest
│   │   └── export.py                  # ExportRow (used for CSV serialization)
│   │
│   ├── routers/                       # FastAPI route handlers — thin, no business logic
│   │   ├── __init__.py
│   │   ├── auth.py                    # POST /auth/register, POST /auth/login
│   │   ├── documents.py               # POST /documents/upload, GET /documents, GET /documents/{id}
│   │   ├── jobs.py                    # POST /jobs/{id}/retry, GET /jobs/{id}/progress/stream
│   │   ├── results.py                 # PATCH /documents/{id}/result, POST /documents/{id}/finalize
│   │   └── export.py                  # GET /documents/{id}/export, GET /export/bulk
│   │
│   ├── services/                      # All business logic and database queries
│   │   ├── __init__.py
│   │   ├── auth_service.py            # register_user, login_user, hash/verify password
│   │   ├── document_service.py        # create_document, list_documents, get_document
│   │   ├── job_service.py             # create_job, get_job, reset_job_for_retry
│   │   ├── result_service.py          # upsert_result, patch_summary, finalize_result
│   │   ├── export_service.py          # build_json_export, stream_csv_rows generator
│   │   └── event_publisher.py         # publish_and_persist — dual DB+Redis write helper
│   │
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py                    # get_current_user FastAPI dependency
│   │
│   └── workers/
│       ├── __init__.py
│       ├── celery_app.py              # Celery app instance, broker/backend config
│       └── tasks.py                   # analyze_document task — full pipeline
│
├── services/
│   └── analysis_engine.py             # Pure Python — no I/O, all SEO computation logic
│
├── tests/
│   ├── conftest.py                    # Shared fixtures: test DB, test client, auth_headers
│   ├── unit/
│   │   ├── test_analysis_engine.py
│   │   └── test_event_publisher.py
│   ├── integration/
│   │   ├── test_worker_pipeline.py
│   │   └── test_retry_idempotency.py
│   └── api/
│       ├── test_auth.py
│       ├── test_upload.py
│       ├── test_documents.py
│       ├── test_job_detail.py
│       ├── test_retry.py
│       ├── test_result.py
│       ├── test_finalize.py
│       ├── test_export.py
│       └── test_progress_stream.py
│
├── alembic/
│   ├── env.py                         # Alembic migration environment
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial_schema.py     # Initial migration: users, documents, jobs, results
│
├── alembic.ini
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Frontend — Full File Tree

```
frontend/
├── src/
│   ├── app/                           # Next.js App Router pages
│   │   ├── layout.tsx                 # Root layout — AuthProvider, QueryProvider wrapping
│   │   ├── page.tsx                   # Root redirect — sends to /login or /dashboard
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx           # Login page
│   │   │   └── register/
│   │   │       └── page.tsx           # Register page
│   │   ├── dashboard/
│   │   │   └── page.tsx               # Jobs dashboard — document list, filters, search
│   │   ├── documents/
│   │   │   └── [id]/
│   │   │       └── page.tsx           # Document detail — review, edit summary, finalize
│   │   └── api/
│   │       └── auth/
│   │           └── session/
│   │               └── route.ts       # Next.js API route — sets httpOnly JWT cookie
│   │
│   ├── components/
│   │   ├── ui/                        # shadcn/ui primitives — never modified directly
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── toast.tsx
│   │   │
│   │   └── features/                  # Feature-level components — use shadcn primitives
│   │       ├── auth/
│   │       │   ├── LoginForm.tsx      # Controlled form — calls POST /auth/login
│   │       │   └── RegisterForm.tsx   # Controlled form — calls POST /auth/register
│   │       ├── upload/
│   │       │   ├── UploadZone.tsx     # File drag-and-drop input with client validation
│   │       │   └── UploadProgress.tsx # HTTP transfer progress bar (axios onUploadProgress)
│   │       ├── dashboard/
│   │       │   ├── DocumentTable.tsx  # Paginated table — columns, badges, action buttons
│   │       │   ├── StatusBadge.tsx    # Color-coded badge for queued/processing/completed/failed/finalized
│   │       │   ├── FilterBar.tsx      # Search input + status filter dropdown + sort controls
│   │       │   └── JobProgressBar.tsx # Per-row live progress bar driven by SSE store state
│   │       ├── detail/
│   │       │   ├── MetricsPanel.tsx   # Word count, readability score, Flesch label display
│   │       │   ├── KeywordsTable.tsx  # Sortable keyword/count/density table
│   │       │   ├── SummaryEditor.tsx  # Textarea + Save Draft button
│   │       │   └── FinalizeButton.tsx # Finalize CTA — disabled until result exists
│   │       └── export/
│   │           └── ExportButtons.tsx  # JSON + CSV download triggers via blob URL
│   │
│   ├── store/                         # Zustand global state
│   │   ├── documentStore.ts           # Document list, pagination, filter state
│   │   └── progressStore.ts           # Per-job progress state updated by SSE hook
│   │
│   ├── hooks/                         # Custom React hooks
│   │   ├── useSSE.ts                  # EventSource wrapper — connects, parses, updates progressStore
│   │   ├── useDocuments.ts            # Fetches paginated document list, exposes refetch
│   │   ├── useDocumentDetail.ts       # Fetches single document + result
│   │   └── useAuth.ts                 # Reads auth context, exposes login/logout/register
│   │
│   ├── lib/
│   │   ├── api.ts                     # Axios instance — base URL, Bearer token interceptor
│   │   └── utils.ts                   # cn() classname utility, date formatters
│   │
│   ├── context/
│   │   └── AuthContext.tsx            # JWT state, login/logout, redirect logic
│   │
│   └── types/
│       ├── document.ts                # Document, ProcessingJob, ExtractedResult TypeScript types
│       └── auth.ts                    # User, TokenResponse types
│
├── public/
├── tailwind.config.ts
├── tsconfig.json
├── next.config.ts
├── components.json                    # shadcn/ui config
└── package.json
```

---

## Backend Module Reference

---

### `app/main.py` — FastAPI Application Factory

This is the entry point of the FastAPI application. It instantiates the `FastAPI` app object and is responsible for registering all routers, configuring CORS middleware, and wiring up the async database lifespan context.

On startup the lifespan handler runs `async_engine.connect()` to verify the database connection is alive. On shutdown it disposes of the connection pool cleanly. CORS is configured to allow the Next.js frontend origin (read from environment) with `allow_credentials=True` so the `Authorization` header is permitted cross-origin.

All routers are registered under the `/api/v1` prefix. The `auth` router is mounted without any auth dependency at the router level — individual route protection is handled per-route via the `get_current_user` dependency. All other routers have the `get_current_user` dependency applied at the router level using `dependencies=[Depends(get_current_user)]` so every route in those routers is automatically protected without needing to repeat the dependency on each function signature.

---

### `app/config.py` — Settings

Uses Pydantic `BaseSettings` to read all configuration from environment variables with full type validation. Every secret and connection string the app needs is defined here as a typed field — `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM` (default `HS256`), `JWT_EXPIRY_HOURS` (default `24`), `UPLOAD_DIR` (default `./storage/uploads`), `MAX_UPLOAD_SIZE_BYTES` (default `5242880` — 5MB), `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`.

No code anywhere else in the backend imports environment variables directly. Everything goes through `from app.config import settings`. This makes configuration testable and prevents scattered `os.getenv()` calls.

---

### `app/database.py` — Database Engine and Session Factory

Creates the async SQLAlchemy engine using `create_async_engine` with the `asyncpg` driver pointed at the Neon PostgreSQL connection string from `settings.DATABASE_URL`. The connection pool is sized for the expected concurrency — `pool_size=5`, `max_overflow=10`.

Exports `AsyncSessionLocal` — an `async_sessionmaker` factory that produces `AsyncSession` instances. Exports `Base` — the `DeclarativeBase` all ORM models inherit from. Exports `get_db` — an `asynccontextmanager` generator function used as a FastAPI dependency that yields a session and guarantees `commit()` on success or `rollback()` on exception, then `close()` unconditionally in the `finally` block.

---

### `app/models/user.py` — User ORM Model

Defines the `users` table. Columns: `id` (UUID primary key, server default `gen_random_uuid()`), `email` (String, unique, not null, indexed), `hashed_password` (String, not null), `is_active` (Boolean, server default `true`, not null), `created_at` (DateTime with timezone, server default `now()`).

Has a relationship to `documents` with `back_populates="user"`. The `email` column has a unique index defined at the model level using `UniqueConstraint` so the database enforces uniqueness independently of application-level checks.

---

### `app/models/document.py` — Document ORM Model

Defines the `documents` table. Columns: `id` (UUID PK), `user_id` (UUID FK → `users.id`, not null, indexed), `original_filename` (String, not null), `file_path` (String, not null), `file_size` (BigInteger, not null), `mime_type` (String, not null), `upload_timestamp` (DateTime TZ, not null), `created_at` (DateTime TZ, server default `now()`).

Has a relationship to `user` with `back_populates="documents"`, a one-to-many relationship to `processing_jobs`, and a one-to-one relationship to `extracted_result` via `uselist=False`.

The `file_path` column stores the absolute path to the uploaded file on the shared bind mount. The `user_id` foreign key is indexed so that the `WHERE user_id = :id` ownership filter on every list query is served by an index scan.

---

### `app/models/processing_job.py` — ProcessingJob ORM Model

Defines the `processing_jobs` table. Columns: `id` (UUID PK), `document_id` (UUID FK → `documents.id`, not null, indexed), `celery_task_id` (String, nullable — null until task is dispatched), `status` (String, not null, default `queued` — enum values: `queued`, `processing`, `completed`, `failed`, `finalized`), `progress_percentage` (Integer, not null, default `0`), `current_stage` (String, not null, default `job_queued`), `error_message` (Text, nullable), `retry_count` (Integer, not null, default `0`), `meta` (JSONB, nullable — stores intermediate parsing stats), `started_at` (DateTime TZ, nullable), `completed_at` (DateTime TZ, nullable), `created_at` (DateTime TZ, server default `now()`).

The `status` column is indexed. Filtering the dashboard by status is a frequent query pattern so the index is load-bearing.

---

### `app/models/extracted_result.py` — ExtractedResult ORM Model

Defines the `extracted_results` table. Columns: `id` (UUID PK), `document_id` (UUID FK → `documents.id`, **unique**, not null), `job_id` (UUID FK → `processing_jobs.id`, not null — always the most recent successful job), `word_count` (Integer, not null), `readability_score` (Float, not null), `primary_keywords` (JSONB, not null — array of `{keyword, count, density_percentage}` objects), `auto_summary` (Text, not null), `user_edited_summary` (Text, nullable — null until user saves a draft), `is_finalized` (Boolean, not null, default `false`), `finalized_at` (DateTime TZ, nullable), `created_at` (DateTime TZ, server default `now()`), `updated_at` (DateTime TZ, onupdate `now()`).

The `UniqueConstraint` on `document_id` is the foundation of the upsert strategy. The database enforces one result per document. Any `INSERT` that would violate this constraint is automatically converted to an `UPDATE` via the `ON CONFLICT` clause, making the worker fully idempotent on retries.

---

### `app/schemas/` — Pydantic v2 DTOs

All schemas use `model_config = ConfigDict(from_attributes=True)` so they can be instantiated from SQLAlchemy ORM objects via `model_validate(orm_obj)`. Schemas are never imported into ORM model files — the dependency flows one direction only: schemas depend on models, models never depend on schemas.

`auth.py` defines `RegisterRequest` (email: EmailStr, password: str with `min_length=8`), `LoginRequest` (email: EmailStr, password: str), `TokenResponse` (access_token: str, token_type: Literal["bearer"]), `UserResponse` (id: UUID, email: str).

`document.py` defines `DocumentResponse` (all document fields plus nested `JobResponse`), `DocumentListResponse` (items: list[DocumentResponse], total: int, page: int, page_size: int).

`job.py` defines `JobResponse` (id, document_id, status, progress_percentage, current_stage, error_message, retry_count, started_at, completed_at), `JobStatusResponse` (minimal — just status and progress for the dashboard table).

`result.py` defines `ExtractedResultResponse` (all result fields), `PatchResultRequest` (user_edited_summary: str — the only patchable field).

`export.py` defines `ExportRow` — a flat Pydantic model used by `csv.DictWriter` with string-serialized versions of all result fields including a comma-joined keyword string.

---

### `app/routers/auth.py` — Auth Routes

Contains exactly two route functions: `register` and `login`. Both are POST endpoints. Neither injects `get_current_user` — they are the only unprotected routes in the application.

`register` calls `auth_service.register_user(db, request.email, request.password)`. If the service raises a `DuplicateEmailError` the router catches it and returns `HTTPException(409)`. On success returns `UserResponse` with status `201`.

`login` calls `auth_service.login_user(db, request.email, request.password)`. If the service raises `InvalidCredentialsError` the router returns `HTTPException(401)` with a deliberately vague message that does not indicate whether the email or password was wrong. On success returns `TokenResponse` with status `200`.

Route handlers are 10–15 lines each. All meaningful logic is in `auth_service`.

---

### `app/routers/documents.py` — Document Routes

Contains three route functions: `upload_documents`, `list_documents`, `get_document`.

`upload_documents` accepts `files: list[UploadFile]` and `current_user: User = Depends(get_current_user)`. It iterates over each file, calls `document_service.save_and_create(db, file, current_user.id)` which handles filesystem write and DB record creation, then calls `job_service.create_and_dispatch(db, document_id)` which creates the `ProcessingJob` row and calls `analyze_document.delay(...)`. Returns the list of `{document_id, job_id}` pairs with status `201`. No processing logic exists in this function.

`list_documents` accepts query parameters `search`, `status`, `sort_by`, `sort_order`, `page`, `page_size` and delegates entirely to `document_service.list_documents(db, user_id=current_user.id, **filters)`. Returns `DocumentListResponse`.

`get_document` calls `document_service.get_document(db, document_id, user_id=current_user.id)`. If the service returns `None` (document not found or belongs to another user) the router raises `HTTPException(404)`. Returns `DocumentResponse`.

---

### `app/routers/jobs.py` — Job Routes

Contains two route functions: `retry_job` and `stream_progress`.

`retry_job` is `POST /jobs/{job_id}/retry`. It calls `job_service.get_job(db, job_id, user_id=current_user.id)` — returns `404` if not found or not owned. If `job.status != "failed"` returns `HTTPException(400, "Only failed jobs can be retried")`. Otherwise calls `job_service.reset_and_redispatch(db, celery_app, job)` which performs the revoke-reset-redispatch sequence. Returns `JobResponse` with status `200`.

`stream_progress` is `GET /jobs/{job_id}/progress/stream`. Returns `StreamingResponse` with `media_type="text/event-stream"`. The response body is an async generator function `event_generator()` defined inline. The generator first verifies ownership via `job_service.get_job`, then checks terminal state — if terminal it yields one final event and returns. If not terminal it opens a Redis Pub/Sub subscriber via `event_publisher.subscribe_to_job(job_id)` inside a `try/finally` block, enters the async message loop, yields each event as `data: {json}\n\n` formatted SSE frames, and exits when a terminal event is received or the client disconnects.

---

### `app/routers/results.py` — Result Routes

Contains two route functions: `patch_result` and `finalize_document`.

`patch_result` is `PATCH /documents/{document_id}/result`. Accepts `PatchResultRequest` body. Calls `result_service.patch_summary(db, document_id, user_id=current_user.id, summary=request.user_edited_summary)`. Returns `ExtractedResultResponse`.

`finalize_document` is `POST /documents/{document_id}/finalize`. Calls `result_service.finalize(db, document_id, user_id=current_user.id)`. The service raises typed errors for 409 (already finalized) and 400 (job ID mismatch) — the router maps these to the appropriate HTTP status codes. Returns `ExtractedResultResponse`.

---

### `app/routers/export.py` — Export Routes

Contains two route functions: `export_document` and `bulk_export`.

`export_document` is `GET /documents/{document_id}/export`. Accepts `format: Literal["json", "csv"] = "json"` as a query param. Verifies ownership and finalization status — returns `403` if not finalized. For JSON calls `export_service.build_json_export(result)` and returns `Response` with `application/json` content type and `Content-Disposition: attachment` header. For CSV constructs a `StringIO` buffer and returns `Response` with `text/csv`.

`bulk_export` is `GET /export/bulk`. Only supports `format=csv`. Returns `StreamingResponse` wrapping `export_service.stream_csv_rows(db, user_id=current_user.id)` — a Python async generator that yields CSV rows one at a time. The `StreamingResponse` sets `Content-Type: text/csv` and a `Content-Disposition` header with a timestamped filename. Memory usage is constant regardless of how many finalized documents the user has because the generator fetches results in batches using `LIMIT/OFFSET` internally.

---

### `app/services/auth_service.py` — Auth Service

`register_user(db, email, password)`: Queries the `users` table for an existing row with the given email. If found raises `DuplicateEmailError`. Otherwise hashes the password using `passlib.hash.bcrypt.hash(password)`, creates a `User` ORM instance, adds it to the session, commits, and returns the `User`.

`login_user(db, email, password)`: Fetches the user by email. If not found or `passlib.hash.bcrypt.verify(password, user.hashed_password)` returns `False`, raises `InvalidCredentialsError`. Otherwise generates a JWT using `python-jose`'s `jwt.encode` with payload `{"sub": str(user.id), "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)}` and returns the token string.

Both functions use custom exception classes defined in `app/exceptions.py` so the router can catch typed errors instead of catching generic `Exception`.

---

### `app/services/document_service.py` — Document Service

`save_and_create(db, file, user_id)`: Reads the file bytes from the `UploadFile` object. Validates file size against `settings.MAX_UPLOAD_SIZE_BYTES` — raises `FileTooLargeError` if exceeded. Validates MIME type is `text/plain` — raises `InvalidFileTypeError` if not. Generates a UUID, constructs the storage path `{UPLOAD_DIR}/{uuid}_{secure_filename}`, writes bytes to disk using standard `pathlib.Path.write_bytes`. Creates a `Document` ORM instance with all metadata fields, commits to DB, returns the `Document`.

`list_documents(db, user_id, search, status, sort_by, sort_order, page, page_size)`: Builds a SQLAlchemy `select` statement with `JOIN` to `processing_jobs`. Applies `WHERE documents.user_id = user_id` unconditionally. Applies `ILIKE` search on `original_filename` if `search` is provided. Applies `WHERE processing_jobs.status = status` if `status` is provided. Applies `ORDER BY` on the requested column. Applies `LIMIT` and `OFFSET` for pagination. Executes two queries — one for the data page and one `SELECT COUNT(*)` with the same filters for the total. Returns both.

`get_document(db, document_id, user_id)`: Fetches a single `Document` joined with its latest `ProcessingJob` and `ExtractedResult` (via `selectinload` to avoid N+1). Applies `WHERE documents.id = document_id AND documents.user_id = user_id`. Returns `None` if nothing matches so the router can return `404`.

---

### `app/services/job_service.py` — Job Service

`create_and_dispatch(db, document_id)`: Creates a `ProcessingJob` row with `status=queued`, `progress_percentage=0`, `current_stage=job_queued`. Flushes to DB to get the generated `id`. Calls `analyze_document.delay(str(job.id), str(document_id), file_path)`. Writes the returned Celery task ID back to `job.celery_task_id`. Commits. Returns the job.

`get_job(db, job_id, user_id)`: Fetches `ProcessingJob` joined through `Document` to verify `documents.user_id = user_id`. Returns `None` if not found or not owned.

`reset_and_redispatch(db, celery_app, job)`: Calls `celery_app.control.revoke(job.celery_task_id, terminate=True)` first. Then updates the job fields: `status=queued`, `progress_percentage=0`, `current_stage=job_queued`, `error_message=None`, `retry_count=0`, `started_at=None`, `completed_at=None`. Dispatches a new `analyze_document.delay(...)`. Writes the new task ID to `celery_task_id`. Commits. Returns the updated job.

---

### `app/services/result_service.py` — Result Service

`patch_summary(db, document_id, user_id, summary)`: Verifies document ownership via a join query. Fetches the `ExtractedResult` by `document_id`. Updates only `user_edited_summary = summary` and `updated_at = now()`. Commits. Returns the result.

`finalize(db, document_id, user_id)`: Verifies document ownership. Fetches the result and the latest `ProcessingJob` for the document. If `result.is_finalized` is already `True` raises `AlreadyFinalizedError`. If `result.job_id != latest_job.id` raises `StaleResultError` — the result is from an older run and should not be finalized while a newer job exists. Otherwise sets `is_finalized=True`, `finalized_at=now()`, and `latest_job.status=finalized`. Commits. Returns the result.

---

### `app/services/export_service.py` — Export Service

`build_json_export(result)`: Takes an `ExtractedResult` ORM object. Constructs a flat Python dict with all fields, serializes `primary_keywords` from JSONB to a Python list, and returns the dict. The router handles `json.dumps` and response construction.

`stream_csv_rows(db, user_id)`: An async generator. Runs a paginated query in batches of 100 rows at a time using `LIMIT/OFFSET` against `extracted_results` joined to `documents` filtered by `user_id` and `is_finalized=True`. On the first iteration yields the CSV header row as a string. On each subsequent iteration yields one data row as a CSV-formatted string using `csv.DictWriter` against a per-row `StringIO`. This pattern keeps memory bounded regardless of total result count.

---

### `app/services/event_publisher.py` — Event Publisher

`publish_and_persist(db, redis_client, job_id, stage, progress, message)`: The most critical function in the worker pipeline. Executes two operations in sequence. First updates `ProcessingJob` in the database — sets `progress_percentage=progress` and `current_stage=stage`. Commits the session. Second publishes a JSON-encoded event to the Redis Pub/Sub channel `job_progress:{job_id}` using `redis_client.publish`. The JSON payload is `{"job_id": job_id, "stage": stage, "progress": progress, "message": message, "timestamp": utcnow().isoformat()}`. If the Redis publish raises an exception it is caught and logged — a Redis failure must never crash the worker pipeline.

`subscribe_to_job(job_id)`: Returns a Redis Pub/Sub subscriber object already subscribed to `job_progress:{job_id}`. Used by the SSE endpoint. The caller is always responsible for unsubscribing in a `try/finally`.

---

### `app/dependencies/auth.py` — Auth Dependency

`get_current_user(authorization: str = Header(None), db: AsyncSession = Depends(get_db))`: Reads the raw `Authorization` header. If missing or not starting with `Bearer ` raises `HTTPException(401)`. Strips the prefix and decodes the JWT using `jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])`. Catches `JWTError` and `ExpiredSignatureError` from `python-jose` and raises `HTTPException(401)` for both. Extracts `user_id` from the `sub` claim. Fetches the `User` from the database. If not found or `user.is_active` is `False` raises `HTTPException(401)`. Returns the `User` object.

This function is the single point of authentication enforcement for the entire API. It is injected at the router level for all non-auth routers.

---

### `app/workers/celery_app.py` — Celery Application

Instantiates the `Celery` object with the app name `seo_analyzer`. Configures `broker_url` and `result_backend` from `settings.CELERY_BROKER_URL` and `settings.CELERY_RESULT_BACKEND` — both point to the Redis instance. Sets `task_serializer="json"`, `result_serializer="json"`, `accept_content=["json"]`. Sets `task_track_started=True` so the `STARTED` state is published to the result backend, enabling the dashboard to distinguish queued from actively running tasks.

The `celery_app` instance is imported by both `workers/tasks.py` (to define tasks) and `job_service.py` (to call `control.revoke` on manual retry).

---

### `app/workers/tasks.py` — Celery Task

Defines the `analyze_document` Celery task with `@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)`. The `bind=True` gives access to `self` for calling `self.retry()` on failure.

The task function signature is `analyze_document(self, job_id: str, document_id: str, file_path: str)`. The body opens a synchronous SQLAlchemy session (the worker is not async — Celery workers use sync sessions), opens a Redis client, and executes the full processing pipeline wrapped in a try/except block.

On any unhandled exception it calls `self.retry(exc=exc)` up to `max_retries` times. On the final failure after all retries are exhausted, the `on_failure` method (decorated with `@analyze_document.on_failure`) is called — it opens a fresh DB session, sets `job.status=failed` and `job.error_message` to the full traceback, and commits.

The pipeline stages inside the task are linear and sequential. Each stage calls `publish_and_persist` immediately after its computation completes. The task never returns a value — all state lives in the database and is communicated to clients via Redis Pub/Sub events.

**Stage sequence inside the task:**
1. Update status to `processing`, set `started_at`, call `publish_and_persist(stage=job_started, progress=5)`.
2. Read and clean file content from `file_path`. Call `publish_and_persist(stage=document_parsing_started, progress=10)`.
3. Extract structural metadata. Call `publish_and_persist(stage=document_parsing_completed, progress=30)`.
4. Call `publish_and_persist(stage=field_extraction_started, progress=35)`.
5. Call `analysis_engine.compute_all(text)` — returns all SEO metrics.
6. Call `publish_and_persist(stage=field_extraction_completed, progress=80)`.
7. Execute the upsert SQL with `COALESCE` protection. Call `publish_and_persist(stage=final_result_stored, progress=90)`.
8. Set `status=completed`, `completed_at=now()`. Call `publish_and_persist(stage=job_completed, progress=100)`.

---

### `services/analysis_engine.py` — Pure Analysis Engine

This module has zero imports from `app/` and zero I/O operations. It is a collection of pure functions that accept a string and return computed values. This design makes it independently unit-testable and reusable.

`compute_word_count(text: str) -> int`: Splits on whitespace, filters tokens where `token.strip(string.punctuation)` is non-empty, returns count.

`compute_readability_score(text: str) -> float`: Splits text into sentences. For each sentence splits into words and counts syllables per word by counting vowel groups using a regex. Computes Flesch Reading Ease as `206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)`. Clamps result to `[0.0, 100.0]`.

`compute_primary_keywords(text: str, top_n: int = 10) -> list[dict]`: Tokenizes, lowercases, strips punctuation from each token, removes tokens in the hardcoded `STOPWORDS` set (defined as a module-level frozenset of ~150 common English words), counts frequency using `collections.Counter`, computes density as `count / total_tokens * 100`. Returns the top `top_n` as a list of `{"keyword": str, "count": int, "density_percentage": float}` dicts.

`compute_summary(text: str) -> str`: Splits the cleaned text on sentence-ending punctuation using `re.split(r'(?<=[.!?])\s+', text)`. Takes the first 3 non-empty sentences, strips whitespace from each, joins with a space. Returns the result as a single string.

`compute_all(text: str) -> dict`: Calls all four functions and returns a single dict with keys `word_count`, `readability_score`, `primary_keywords`, `auto_summary`. This is the only function the worker task calls — it does not call individual functions directly.

---

## Frontend Module Reference

---

### `src/app/layout.tsx` — Root Layout

Wraps the entire application with `AuthProvider` (from `context/AuthContext.tsx`) and a `Toaster` component from shadcn/ui for global toast notifications. Sets the HTML `lang` attribute and base font via Tailwind. Does not contain any page-level UI — it is purely a provider wrapper.

---

### `src/app/api/auth/session/route.ts` — Session Cookie Route

A Next.js Route Handler that receives `POST` requests from the frontend after a successful login. Accepts `{ token: string }` in the JSON body. Uses Next.js `cookies()` to set a `jwt` cookie with `httpOnly: true`, `secure: true` (in production), `sameSite: "lax"`, and a `maxAge` matching the 24-hour JWT expiry. Returns `{ ok: true }`. Also handles `DELETE` to clear the cookie on logout.

This indirection exists because `httpOnly` cookies cannot be set from client-side JavaScript. All cookie management goes through this server-side route handler.

---

### `src/context/AuthContext.tsx` — Auth Context

Defines `AuthContext` with `{ user, isLoading, login, logout, register }`. On mount it reads the `jwt` cookie via a `GET /api/auth/session` call to check if a valid session exists. If a JWT is found it decodes the payload client-side (without signature verification — just to read the `user_id` and `email` claims for display) and sets `user`.

`login(email, password)`: Calls `POST /api/v1/auth/login`, passes the returned token to `POST /api/auth/session` to set the `httpOnly` cookie, updates context state.

`logout()`: Calls `DELETE /api/auth/session` to clear the cookie, resets `user` to null, pushes to `/login`.

`register(email, password)`: Calls `POST /api/v1/auth/register`, on success calls `login` automatically.

Any component wrapped in a page that requires auth uses `useAuth()` and redirects to `/login` if `user` is null and `isLoading` is false.

---

### `src/store/documentStore.ts` — Document Zustand Store

Manages the global document list state used by the dashboard. State shape: `{ documents: DocumentResponse[], total: int, page: int, pageSize: int, filters: { search: string, status: string, sortBy: string, sortOrder: string }, isLoading: bool, error: string | null }`.

Actions: `setDocuments`, `setFilters`, `setPage`, `setLoading`, `setError`. The `setFilters` action resets `page` to 1 automatically since changing a filter invalidates the current page position.

The store does not fetch data directly — it holds the result of fetches initiated by the `useDocuments` hook. The separation keeps the store as pure state and keeps data fetching logic in hooks.

---

### `src/store/progressStore.ts` — Progress Zustand Store

Manages per-job live progress state driven by the SSE stream. State shape: `{ progress: Record<string, { stage: string, percentage: number, message: string }> }`.

Actions: `updateJobProgress(jobId, event)` — merges the incoming SSE event into the `progress` map for the given job ID. `clearJobProgress(jobId)` — removes a job's entry when the detail page unmounts.

This store is the bridge between the SSE hook and the UI components. The `JobProgressBar` component in the dashboard reads `progressStore.progress[jobId]` and re-renders whenever it updates.

---

### `src/hooks/useSSE.ts` — SSE Hook

`useSSE(jobId: string | null)`: Opens a connection to `GET /api/v1/jobs/{jobId}/progress/stream` using the browser's native `EventSource` API when `jobId` is non-null.

On each `message` event it parses the JSON payload and calls `progressStore.updateJobProgress(jobId, parsedEvent)`.

On receiving a terminal event (`stage === "job_completed"` or `stage === "job_failed"`) it closes the `EventSource` connection and calls `documentStore` to trigger a re-fetch of the document list so the status badge updates.

In the cleanup function returned from `useEffect`, it calls `eventSource.close()` to prevent leaking connections when the component unmounts.

The `EventSource` API does not support custom headers, which means the JWT cannot be sent as a `Bearer` token. The SSE endpoint reads auth from a query parameter `?token=` for this reason — the hook appends the token from `AuthContext` to the URL. The backend `stream_progress` handler accepts either the `Authorization` header or the `token` query param, preferring the header.

---

### `src/hooks/useDocuments.ts` — Documents Hook

Uses a `useEffect` to watch `documentStore.filters` and `documentStore.page`. On change, sets `isLoading=true`, calls `api.get("/documents", { params: { ...filters, page, page_size } })`, and on success calls `documentStore.setDocuments(data.items, data.total)`. Exposes a `refetch()` function for manual refresh triggers (e.g., after retry or upload).

Sets up a `setInterval` of 5000ms to call `refetch()` automatically for coarse status polling of the dashboard table — this keeps status badges up to date for jobs the user is not actively watching via SSE.

Clears the interval in the `useEffect` cleanup.

---

### `src/hooks/useDocumentDetail.ts` — Document Detail Hook

Fetches a single document's full data on mount using the `document_id` from the page route params. Calls `GET /api/v1/documents/{id}`. Exposes `document`, `job`, `result`, `isLoading`, `refetch`. The detail page calls `refetch()` after Save Draft and after Finalize to refresh the displayed data.

---

### `src/lib/api.ts` — Axios Instance

Creates a single Axios instance with `baseURL` set to `process.env.NEXT_PUBLIC_API_URL`. Defines a request interceptor that reads the JWT from the `AuthContext` (accessed via a module-level reference, not a hook — hooks cannot be used inside interceptors) and appends `Authorization: Bearer {token}` to every outbound request. Defines a response interceptor that catches `401` responses and triggers `AuthContext.logout()` to clear the session and redirect to login — this handles expired tokens gracefully without requiring per-request error handling.

---

### `src/components/features/upload/UploadZone.tsx`

Renders a drag-and-drop area using HTML5 drag events and a hidden `<input type="file" multiple accept=".txt">`. On file selection, runs client-side validation — checks each file's `type === "text/plain"` and `size <= 5242880`. Invalid files get an inline error message. Valid files are batched into a `FormData` object and sent via `api.post("/documents/upload", formData, { onUploadProgress })`. The `onUploadProgress` callback updates a local `uploadPercent` state that drives `UploadProgress.tsx`. On success, extracts the returned `{ document_id, job_id }` pairs and calls `useSSE` for each job ID to begin live progress tracking.

---

### `src/components/features/dashboard/DocumentTable.tsx`

Renders a `shadcn/ui` `Table` with columns: Filename, Uploaded, Status, Progress, Actions. The Status column renders `StatusBadge`. The Progress column renders `JobProgressBar` which reads from `progressStore` — it only shows for jobs with `status === "processing"` and is hidden otherwise. The Actions column renders icon buttons: an eye icon linking to `/documents/{id}` for all rows, a refresh icon calling `POST /jobs/{id}/retry` for `failed` rows, and a download icon opening the export flow for `finalized` rows.

Pagination controls sit below the table — previous/next buttons and a page indicator — connected to `documentStore.setPage`.

---

### `src/components/features/detail/SummaryEditor.tsx`

Renders a `shadcn/ui` `Textarea` pre-populated with `result.user_edited_summary ?? result.auto_summary`. When `result.is_finalized` is true the textarea is `disabled` and a "Finalized — read only" label appears instead of the Save Draft button.

When not finalized: tracks edit state in local `useState`. The Save Draft button is only enabled when the current value differs from the initial value (dirty check). On click calls `api.patch("/documents/{id}/result", { user_edited_summary: value })` and shows a success toast on completion.

---

## Configuration & Infrastructure Files

---

### `docker-compose.yml`

Defines four services: `api`, `worker`, `db`, `redis`.

`api`: Builds from `backend/Dockerfile`. Runs `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`. Mounts `./storage/uploads:/app/storage/uploads`. Exposes port `8000`. Depends on `db` and `redis`. Reads environment from `.env`.

`worker`: Same image as `api` — built from the same `backend/Dockerfile`. Runs `celery -A app.workers.celery_app worker --loglevel=info`. Mounts `./storage/uploads:/app/storage/uploads` — the critical shared bind mount that allows the worker to access uploaded files. Depends on `db` and `redis`. Reads environment from `.env`.

`db`: Uses `postgres:16-alpine`. Mounts a named volume for persistence. Exposes port `5432`. Used only for local development — production uses Neon.

`redis`: Uses `redis:7-alpine`. Exposes port `6379`. Used as both the Celery broker and the Pub/Sub event bus.

Both `api` and `worker` share the same `./storage/uploads` bind mount path. This is the architectural decision that makes local single-node deployment work without an object storage service.

---

### `backend/Dockerfile`

Uses `python:3.11-slim` as the base. Installs system dependencies for `asyncpg` and `bcrypt`. Copies `requirements.txt` and runs `pip install --no-cache-dir -r requirements.txt`. Copies the application code. Sets `WORKDIR /app`. Does not set a default `CMD` — the command is specified per-service in `docker-compose.yml`.

---

### `backend/alembic/versions/0001_initial_schema.py`

Creates all four tables in order: `users`, `documents`, `processing_jobs`, `extracted_results`. The `extracted_results` table creation includes `UniqueConstraint("document_id")` explicitly as a named constraint `uq_extracted_results_document_id`. Indexes are created on `documents.user_id`, `processing_jobs.document_id`, and `processing_jobs.status`.

---

### `.env.example`

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/seo_analyzer
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=change_this_to_a_long_random_string
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
UPLOAD_DIR=./storage/uploads
MAX_UPLOAD_SIZE_BYTES=5242880
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Test Suite Reference

---

### `tests/conftest.py` — Shared Fixtures

`test_db_session`: Creates an isolated test database session using a separate schema or test database. Yields the session and rolls back all changes after each test using `ROLLBACK` rather than `DELETE` — faster and guarantees full isolation.

`test_client`: Creates an `httpx.AsyncClient` pointed at the FastAPI app with the `get_db` dependency overridden to use `test_db_session`.

`auth_headers`: Calls `POST /api/v1/auth/register` with a fixed test email and password, then `POST /api/v1/auth/login`, extracts the token, and returns `{"Authorization": "Bearer {token}"}`. All endpoint tests that need auth simply include `auth_headers` as a parameter.

`second_user_auth_headers`: Same as `auth_headers` but registers a different email. Used in cross-user isolation tests.

`sample_txt_file`: Returns an `httpx` file upload tuple with a small in-memory `.txt` file containing known text for deterministic analysis assertions.

---

### `tests/unit/test_analysis_engine.py`

Tests `compute_word_count` with a 10-word string, verifies exact return value. Tests with a string of only punctuation, verifies 0. Tests with empty string, verifies 0.

Tests `compute_readability_score` with a simple short sentence, verifies return is float in `[0, 100]`. Tests with a string of very long complex words, verifies score is lower than a simple sentence score.

Tests `compute_primary_keywords` with a string containing 5 repetitions of "python" and 1 of "the" (stopword), verifies "python" is in results and "the" is not. Tests top_n limiting. Tests all-stopword input returns empty list.

Tests `compute_summary` with a 5-sentence string, verifies return contains only 3 sentences. Tests single-sentence input. Tests empty string returns empty string.

Tests `compute_all` returns a dict with all four expected keys and correct types.

---

### `tests/unit/test_event_publisher.py`

Mocks `db.execute`, `db.commit` and `redis_client.publish`. Calls `publish_and_persist(mock_db, mock_redis, job_id, "job_started", 5, "test")`. Asserts `db.execute` was called once with an `UPDATE` statement touching `progress_percentage` and `current_stage`. Asserts `mock_redis.publish` was called once with channel `job_progress:{job_id}` and a JSON string containing `"stage": "job_started"`.

Tests exception isolation: patches `mock_redis.publish` to raise `ConnectionError`. Calls `publish_and_persist`. Asserts no exception propagates out. Asserts the DB commit still happened.

---

### `tests/integration/test_worker_pipeline.py`

Creates `Document` and `ProcessingJob` rows directly in the test DB. Writes a fixture `.txt` file to a temp directory. Calls `analyze_document.apply(args=[job_id, document_id, file_path])` — `apply()` runs the task synchronously in-process without a broker.

Asserts: `ProcessingJob.status == "completed"`, `ProcessingJob.progress_percentage == 100`, `ProcessingJob.completed_at` is not null. Asserts `ExtractedResult` row exists with `word_count > 0`, `readability_score` between 0 and 100, `primary_keywords` is a non-empty list, `auto_summary` is a non-empty string.

Also tests failure path: deletes the fixture file before running the task. Asserts `ProcessingJob.status == "failed"` and `error_message` is non-null after all retries exhaust.

---

### `tests/integration/test_retry_idempotency.py`

Runs `analyze_document.apply(...)` twice on the same document. Queries `SELECT COUNT(*) FROM extracted_results WHERE document_id = :id`. Asserts count equals exactly 1.

Between the two runs, manually sets `extracted_results.user_edited_summary = "custom user summary"` and commits. After the second run, re-fetches the result row and asserts `user_edited_summary == "custom user summary"` — proving the `COALESCE` upsert preserved the edit.

---

### `tests/api/test_auth.py`

Full coverage of the auth endpoints. Key assertions: registering with `password="short"` (7 chars) returns `422`. Logging in with wrong password returns `401`. Calling `GET /api/v1/documents` without a token returns `401`. Calling it with a manually crafted expired JWT returns `401`. Calling `GET /api/v1/documents/{other_user_document_id}` with valid auth of a different user returns `404`.

---

### `tests/api/test_upload.py`

Posts a valid `.txt` file with `auth_headers`. Asserts `201` and response body contains `document_id` (valid UUID) and `job_id` (valid UUID). Posts two files. Asserts response is a list of length 2. Posts a `.pdf` file. Asserts `422`. Posts a file where bytes length exceeds 5MB. Asserts `413`. Posts without auth. Asserts `401`.

---

### `tests/api/test_documents.py`

Seeds 3 documents for `auth_headers` user and 1 for `second_user_auth_headers`. Calls `GET /api/v1/documents` with `auth_headers`. Asserts response total is 3 (not 4 — the second user's document is excluded). Calls with `status=completed` filter after manually setting one job to completed. Asserts only 1 result. Calls with `search=fixture` (matching 2 of 3 filenames). Asserts 2 results. Calls with `sort_by=created_at&sort_order=desc`. Asserts first result has the most recent timestamp.

---

### `tests/api/test_retry.py`

Seeds a job with `status=failed`. Calls `POST /api/v1/jobs/{job_id}/retry`. Asserts `200`. Re-fetches job. Asserts `status == "queued"` and `error_message` is null and `celery_task_id` has changed. Seeds a job with `status=completed`. Calls retry. Asserts `400`. Seeds a job with `status=processing`. Asserts `400`. Calls retry on another user's failed job. Asserts `404`.

---

### `tests/api/test_finalize.py`

Seeds a completed result. Calls `POST /api/v1/documents/{id}/finalize`. Asserts `200`. Re-fetches result. Asserts `is_finalized == True` and `finalized_at` is not null. Calls finalize again on the same document. Asserts `409`. Seeds a completed result but also seeds a second `ProcessingJob` for the same document (simulating a retry that created a newer job) without updating `result.job_id`. Calls finalize. Asserts `400` (stale job ID mismatch). Calls finalize on another user's document. Asserts `404`.

---

### `tests/api/test_export.py`

Seeds a finalized result. Calls `GET /api/v1/documents/{id}/export?format=json`. Asserts `200`, `Content-Type: application/json`, and response JSON contains all expected keys: `word_count`, `readability_score`, `primary_keywords`, `auto_summary`, `user_edited_summary`. Calls with `format=csv`. Asserts `200`, `Content-Type: text/csv`, and CSV string has a header row and one data row. Seeds a non-finalized result. Calls export. Asserts `403`. Seeds 3 finalized results for the same user. Calls `GET /api/v1/export/bulk?format=csv`. Asserts response is valid CSV with exactly 4 lines (1 header + 3 data). Calls export on another user's document. Asserts `404`.

---

### `tests/api/test_progress_stream.py`

Seeds a job with `status=completed`. Connects to `GET /api/v1/jobs/{job_id}/progress/stream`. Reads the response body. Asserts a single `data:` SSE frame is returned containing `"stage": "job_completed"`. Asserts the connection closes after the frame (response body ends). This verifies the terminal-state fast-path — no Redis subscription was opened.

For the live path: seeds a job with `status=processing`. Spawns a background thread that publishes 3 mock events to `job_progress:{job_id}` in Redis with a small delay between each, ending with a `job_completed` event. Connects to the SSE stream. Reads frames as they arrive. Asserts all 3 events are received in order and the connection closes after the terminal event.

Connects without auth. Asserts `401`. Connects to another user's job stream. Asserts `404`.
