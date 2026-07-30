from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.routers import market, analysis, websocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BIST Finansal Analiz Motoru API",
    version="1.0.0",
    description="BIST (Borsa Istanbul) Financial Analysis Engine Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router, prefix="/api/v1/market", tags=["Market"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(websocket.router, tags=["Websocket"])

@app.on_event("startup")
async def startup_event():
    logger.info("BIST Analiz Motoru başlatıldı")

@app.get("/")
async def root():
    return {
        "status": "online",
        "version": "1.0.0",
        "service": "BIST Finansal Analiz Motoru"
    }
