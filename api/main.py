"""
ELARA — FastAPI Main Application
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi                    import FastAPI
from fastapi.middleware.cors    import CORSMiddleware
from contextlib                 import asynccontextmanager
from api.database               import create_tables
from api.services.elara_service import ELARAService
from api.routes                 import assessment, intervention, mission


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting ELARA API...")
    create_tables()
    service = ELARAService.get_instance()
    service.initialize()
    print("ELARA API ready.")
    yield
    # Shutdown
    print("ELARA API shutting down.")


app = FastAPI(
    title       = "ELARA API",
    description = "Silent Intelligence for Astronaut Psychological Resilience",
    version     = "1.0.0",
    lifespan    = lifespan
)

# CORS — allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins       = ["*"],
    allow_credentials   = True,
    allow_methods       = ["*"],
    allow_headers       = ["*"],
)

# Register routes
app.include_router(assessment.router)
app.include_router(intervention.router)
app.include_router(mission.router)


@app.get("/")
def root():
    return {
        "system"    : "ELARA",
        "status"    : "operational",
        "version"   : "1.0.0",
        "mission"   : "Silent Intelligence for Astronaut Psychological Resilience"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}