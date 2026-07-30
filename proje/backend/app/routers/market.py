from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.services.data_fetcher import get_data_fetcher, BaseDataFetcher
from app.services.indicator_engine import calculate_indicators, get_indicator_overlay_data
from app.models.schemas import StockIndicators, StockHistoryResponse, ErrorResponse

router = APIRouter()

async def get_fetcher() -> BaseDataFetcher:
    return get_data_fetcher("yfinance")

@router.get("/stock/{symbol}", response_model=StockIndicators)
async def get_stock_indicators(symbol: str, fetcher: BaseDataFetcher = Depends(get_fetcher)):
    try:
        df = await fetcher.fetch_stock_data(symbol, period="1y", interval="1d")
        indicators = calculate_indicators(df, symbol)
        return indicators
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

@router.get("/indices", response_model=list[dict])
async def get_indices(fetcher: BaseDataFetcher = Depends(get_fetcher)):
    try:
        indices = await fetcher.fetch_indices()
        return indices
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching indices: {str(e)}")

@router.get("/history/{symbol}", response_model=StockHistoryResponse)
async def get_stock_history(
    symbol: str, 
    period: str = "6mo", 
    interval: str = "1d",
    fetcher: BaseDataFetcher = Depends(get_fetcher)
):
    try:
        df = await fetcher.fetch_stock_data(symbol, period=period, interval=interval)
        # Calculate indicators for overlay
        # We compute ta values inline or pass the full dataframe to a helper
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        
        data_points = []
        for idx, row in df.iterrows():
            data_points.append({
                "date": str(idx.date()) if hasattr(idx, 'date') else str(idx),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": int(row["Volume"])
            })
            
        overlays = get_indicator_overlay_data(df)
        
        return StockHistoryResponse(
            symbol=symbol,
            period=period,
            interval=interval,
            data=data_points,
            indicators=overlays
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching history: {str(e)}")
