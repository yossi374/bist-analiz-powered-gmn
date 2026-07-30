from abc import ABC, abstractmethod
import pandas as pd
import yfinance as yf
import asyncio
from typing import List, Dict

class BaseDataFetcher(ABC):
    """Abstract base class for data fetchers. New sources (Finnhub, etc.) implement this."""
    
    @abstractmethod
    async def fetch_stock_data(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        """Fetch OHLCV data for a symbol. Returns DataFrame with Open, High, Low, Close, Volume columns."""
        pass
    
    @abstractmethod
    async def fetch_stock_info(self, symbol: str) -> dict:
        """Fetch basic stock info (name, sector, market_cap, pe_ratio, etc.)"""
        pass
    
    @abstractmethod
    async def fetch_indices(self) -> List[Dict]:
        """Fetch major market indices."""
        pass

class YFinanceDataFetcher(BaseDataFetcher):
    """yfinance implementation. BIST tickers use .IS suffix."""
    
    def _format_symbol(self, symbol: str) -> str:
        symbol = symbol.upper().strip()
        if not symbol.endswith(".IS"):
            symbol += ".IS"
        return symbol
    
    def _fetch_stock_data_sync(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        formatted_symbol = self._format_symbol(symbol)
        ticker = yf.Ticker(formatted_symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            raise ValueError(f"No data found for symbol {formatted_symbol}")
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        # yfinance bazen tz-aware, bazen tz-naive index döndürür; ikisini de yakala
        if df.index.tz is not None:
            df.index = df.index.tz_convert(None)
        return df

    async def fetch_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        return await asyncio.to_thread(self._fetch_stock_data_sync, symbol, period, interval)
    
    def _fetch_stock_info_sync(self, symbol: str) -> dict:
        formatted_symbol = self._format_symbol(symbol)
        ticker = yf.Ticker(formatted_symbol)
        info = ticker.info
        return {
            "name": info.get("shortName", formatted_symbol),
            "sector": info.get("sector", "Unknown"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow")
        }

    async def fetch_stock_info(self, symbol: str) -> dict:
        return await asyncio.to_thread(self._fetch_stock_info_sync, symbol)
    
    def _fetch_indices_sync(self) -> List[Dict]:
        indices = ["XU100.IS", "XU030.IS", "XBANK.IS", "XUSIN.IS"]
        results = []
        for idx in indices:
            try:
                ticker = yf.Ticker(idx)
                info = ticker.fast_info
                last_price = info.get("lastPrice", 0)
                prev_close = info.get("previousClose", 1)
                change = ((last_price - prev_close) / prev_close) * 100 if prev_close else 0
                results.append({
                    "symbol": idx,
                    "last_price": last_price,
                    "change_percent": change
                })
            except Exception:
                pass
        return results

    async def fetch_indices(self) -> List[Dict]:
        return await asyncio.to_thread(self._fetch_indices_sync)

def get_data_fetcher(source: str = "yfinance") -> BaseDataFetcher:
    fetchers = {"yfinance": YFinanceDataFetcher}
    return fetchers[source]()
