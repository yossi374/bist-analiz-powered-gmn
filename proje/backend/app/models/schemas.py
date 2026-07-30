from pydantic import BaseModel
from typing import Optional, List, Dict

class StockPrice(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: str

class StockIndicators(BaseModel):
    symbol: str
    last_price: float
    change_percent: Optional[float] = None
    daily_high: Optional[float] = None
    daily_low: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr_14: Optional[float] = None
    timestamp: str

class HistoryDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class StockHistoryResponse(BaseModel):
    symbol: str
    period: str
    interval: str
    data: List[HistoryDataPoint]
    indicators: Optional[Dict] = None

class AgentAnalysis(BaseModel):
    agent_name: str
    agent_role: str
    analysis_text: str
    signal: str
    confidence: float
    key_points: List[str]

class FullAnalysisResponse(BaseModel):
    symbol: str
    timestamp: str
    indicators: StockIndicators
    technical_analysis: AgentAnalysis
    fundamental_analysis: AgentAnalysis
    risk_assessment: AgentAnalysis
    final_decision: str
    final_confidence: float
    summary: str

class QuickAnalysisResponse(BaseModel):
    symbol: str
    timestamp: str
    rsi_14: Optional[float] = None
    macd_signal_text: str
    trend: str
    quick_signal: str
    summary: str

class WebSocketTickerMessage(BaseModel):
    symbol: str
    price: float
    high: float
    low: float
    volume: float
    change_percent: float
    timestamp: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
