from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from models.common import HealthResponse
from db.pool.db import db_manager
from routes.customers import router as customers_router
from routes.rentals import router as rentals_router
from routes.discounts import router as discount_router
from config.settings import Settings


# Lifespan manager for database connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_manager.init_pool()
    yield
    # Shutdown
    await db_manager.close_pool()


app = FastAPI(
    title="Bowling Shoes Rental Service",
    description="A FastAPI service for managing bowling shoe rentals with LLM-powered discount calculations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customers_router)
app.include_router(rentals_router)
app.include_router(discount_router)


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": Settings.APP_NAME,
        "version": Settings.APP_VERSION,
        "description": Settings.APP_DESCRIPTION,
        "api_key_required": True,
        "api_key_header": "Authorization: Bearer <api_key>",
        "note": "All endpoints require valid API key in Authorization header"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="bowling-shoes-rental")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 