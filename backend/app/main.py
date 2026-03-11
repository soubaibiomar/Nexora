from dotenv import load_dotenv
load_dotenv()  # Load .env vars (OPENAI_API_KEY, etc.) into os.environ

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from .config import get_settings
from .database import Neo4jDriver
from .routers import experts, documents, graph, learning, dashboard, auth, ai, bigdata
from .routers import feed, network, messaging, jobs, notifications
from .routers import learning_resources
from .routers import gamification
from .routers import skillmap
from .routers import workspaces
from .routers import kafka_simulator

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Nexora API...")
    yield
    # Shutdown
    Neo4jDriver.close()
    print("Nexora API shutdown complete.")


app = FastAPI(
    title=settings.app_name,
    description="Knowledge Cartography Platform - Expert Discovery & Learning Paths",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
cors_origins = ["http://localhost:3000", "http://localhost:5173"]
cors_origin_regex = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$" if settings.debug else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(experts.router)
app.include_router(documents.router)
app.include_router(graph.router)
app.include_router(learning.router)
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(bigdata.router)
app.include_router(feed.router)
app.include_router(network.router)
app.include_router(messaging.router)
app.include_router(jobs.router)
app.include_router(notifications.router)
app.include_router(learning_resources.router)
app.include_router(gamification.router)
app.include_router(skillmap.router)
app.include_router(workspaces.router)
app.include_router(kafka_simulator.router)

# Mount uploads directory for serving uploaded media
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Nexora Intelligent API",
        "docs": "/docs",
        "features": [
            "Expert Search with filters",
            "Document Search with NLP",
            "3D Graph Visualization",
            "Learning Path Generation",
            "Analytics Dashboard",
            "AI-Powered Expert Recommendation",
            "Document Auto-Classification",
            "Skill Gap Prediction",
            "AI Chatbot",
            "Big Data Analytics (Spark)",
            "Gamification (Badges & Endorsements)",
            "Real-Time WebSockets",
            "GraphRAG (Natural Language to Cypher)"
        ]
    }


@app.get("/health")
async def health_check():
    try:
        driver = Neo4jDriver.get_driver()
        with driver.session() as session:
            session.run("RETURN 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
