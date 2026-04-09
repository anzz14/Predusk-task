from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.dependencies.auth import get_current_user
from app.routers import auth, documents, jobs, results, export


@asynccontextmanager
async def lifespan(app: FastAPI):
	# Startup: verify database connection
	async with engine.connect() as connection:
		pass  # Connection successful
	yield
	# Shutdown: dispose of connection pool cleanly
	await engine.dispose()


app = FastAPI(
	title="SEO Analyzer API",
	description="Bulk SEO content analyzer API",
	version="1.0.0",
	lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=[settings.FRONTEND_ORIGIN],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(
	documents.router,
	prefix="/api/v1",
	dependencies=[Depends(get_current_user)],
)
app.include_router(
	jobs.router,
	prefix="/api/v1",
	dependencies=[Depends(get_current_user)],
)
app.include_router(
	results.router,
	prefix="/api/v1",
	dependencies=[Depends(get_current_user)],
)
app.include_router(
	export.router,
	prefix="/api/v1",
	dependencies=[Depends(get_current_user)],
)