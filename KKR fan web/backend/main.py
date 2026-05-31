import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from database import init_db, close_db, db_manager
from routes import players, matches, news, quiz, legends, seasons, cheers, poll, auth, admin, websocket
from utils.websocket_manager import manager
from utils.logger import logger

# Retrieve allowed CORS origins dynamically from env variables
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "https://kkr-fan-hub.vercel.app,https://kkr-fan-hub-frontend.vercel.app,http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# Add FRONTEND_URL dynamically to allowed origins for production convenience
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    cleaned_frontend = frontend_url.strip()
    if cleaned_frontend and cleaned_frontend not in allowed_origins:
        allowed_origins.append(cleaned_frontend)

# Retrieve allowed hosts for security hardening
allowed_hosts_str = os.getenv("ALLOWED_HOSTS", "*")
allowed_hosts = [host.strip() for host in allowed_hosts_str.split(",") if host.strip()]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    env_mode = os.getenv("ENVIRONMENT", "development")
    logger.info(f"FastAPI starting up... Running in environment mode: {env_mode}")
    logger.info(f"FastAPI startup: Allowed CORS origins are {allowed_origins}")
    logger.info("FastAPI starting up... Initializing MongoDB connection.")
    try:
        init_db()
        logger.info("MongoDB connection verification complete.")
    except Exception as e:
        logger.critical(f"MongoDB connection check failed during startup: {e}")
        # Reraising halts server startup for visibility in production environments
        raise e
    
    logger.info("WebSocket: Routes initialized on /ws/cheers and /ws/poll")
    logger.info("WebSocket: Rooms initialized: 'cheers', 'poll'")
    yield
    # Shutdown actions
    logger.info("FastAPI shutting down... Cleaning up active WebSockets.")
    try:
        await manager.shutdown()
    except Exception as e:
        logger.error(f"Error during WebSocket manager shutdown: {e}")
    logger.info("FastAPI shutting down... Cleaning up database client.")
    close_db()
    logger.info("Database client disconnected successfully.")

app = FastAPI(
    title="KKR Fan Hub API",
    description="Modular FastAPI backend for Kolkata Knight Riders Fan Web Application with MongoDB Atlas & JWT auth.",
    version="1.0.0",
    lifespan=lifespan
)

# 1. TrustedHostMiddleware for deployment host header hardening
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# 2. GZipMiddleware for response compression (speeds up JSON delivery)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)

# 3. HTTP Cache-Control header middleware for static GET routes
@app.middleware("http")
async def add_cache_control_header(request, call_next):
    response = await call_next(request)
    path = request.url.path
    # Set Cache-Control header (1 hour cache) for read-only static rosters/schedules
    if request.method == "GET" and any(route in path for route in ["/api/players", "/api/legends", "/api/matches", "/api/seasons"]):
        response.headers["Cache-Control"] = "public, max-age=3600"
    return response

# 4. CORS configuration targeted for frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular route routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Dashboard"])
app.include_router(players.router, prefix="/api", tags=["Players & Stats"])
app.include_router(matches.router, prefix="/api", tags=["Matches"])
app.include_router(news.router, prefix="/api", tags=["News"])
app.include_router(quiz.router, prefix="/api", tags=["Quiz"])
app.include_router(legends.router, prefix="/api", tags=["Legends"])
app.include_router(seasons.router, prefix="/api", tags=["Seasons"])
app.include_router(cheers.router, prefix="/api", tags=["Cheers"])
app.include_router(poll.router, prefix="/api", tags=["MVP Poll"])

# Mount websocket router without prefix so paths resolve to /ws/cheers and /ws/poll
app.include_router(websocket.router, tags=["WebSockets"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the KKR Fan Hub FastAPI Backend (MongoDB + JWT)",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint checking database connectivity."""
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database client is not initialized.")
    try:
        # Ping the database to verify active connection
        db_manager.client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database connectivity check failed: {e}")
