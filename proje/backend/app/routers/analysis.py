from fastapi import APIRouter, HTTPException, Depends
from app.services.data_fetcher import get_data_fetcher, BaseDataFetcher
from app.services.indicator_engine import calculate_indicators
from app.services.ai_analyzer import AIAnalyzer
from app.models.schemas import FullAnalysisResponse, QuickAnalysisResponse

router = APIRouter()
analyzer = AIAnalyzer()

async def get_fetcher() -> BaseDataFetcher:
    return get_data_fetcher("yfinance")

@router.post("/full/{symbol}", response_model=FullAnalysisResponse)
async def run_full_analysis(symbol: str, fetcher: BaseDataFetcher = Depends(get_fetcher)):
    try:
        df = await fetcher.fetch_stock_data(symbol, period="1y", interval="1d")
        indicators = calculate_indicators(df, symbol)
        stock_info = await fetcher.fetch_stock_info(symbol)
        
        response = await analyzer.run_full_analysis(symbol, indicators, stock_info)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/quick/{symbol}", response_model=QuickAnalysisResponse)
async def run_quick_analysis(symbol: str, fetcher: BaseDataFetcher = Depends(get_fetcher)):
    try:
        df = await fetcher.fetch_stock_data(symbol, period="1y", interval="1d")
        indicators = calculate_indicators(df, symbol)
        
        response = await analyzer.run_quick_analysis(symbol, indicators)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")
