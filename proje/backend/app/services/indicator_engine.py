import pandas as pd
import pandas_ta as ta
from typing import Dict, List
from app.models.schemas import StockIndicators

def calculate_indicators(df: pd.DataFrame, symbol: str) -> StockIndicators:
    if df.empty:
        raise ValueError("DataFrame is empty, cannot calculate indicators")

    # Note: SMA_200 will be None if less than 200 periods available — this is handled gracefully below.
    # Calculate indicators using pandas-ta
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=50, append=True)
    df.ta.sma(length=200, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.bbands(length=20, std=2, append=True)
    df.ta.atr(length=14, append=True)
    
    # Get last row for current values
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    last_price = float(latest['Close'])
    prev_close = float(prev['Close'])
    change_percent = ((last_price - prev_close) / prev_close) * 100 if prev_close else 0.0

    return StockIndicators(
        symbol=symbol,
        last_price=last_price,
        change_percent=change_percent,
        daily_high=float(latest.get('High', last_price)),
        daily_low=float(latest.get('Low', last_price)),
        sma_20=float(latest.get('SMA_20', 0)) if not pd.isna(latest.get('SMA_20')) else None,
        sma_50=float(latest.get('SMA_50', 0)) if not pd.isna(latest.get('SMA_50')) else None,
        sma_200=float(latest.get('SMA_200', 0)) if not pd.isna(latest.get('SMA_200')) else None,
        rsi_14=float(latest.get('RSI_14', 0)) if not pd.isna(latest.get('RSI_14')) else None,
        macd=float(latest.get('MACD_12_26_9', 0)) if not pd.isna(latest.get('MACD_12_26_9')) else None,
        macd_signal=float(latest.get('MACDs_12_26_9', 0)) if not pd.isna(latest.get('MACDs_12_26_9')) else None,
        macd_hist=float(latest.get('MACDh_12_26_9', 0)) if not pd.isna(latest.get('MACDh_12_26_9')) else None,
        bollinger_upper=float(latest.get('BBU_20_2.0_2.0', 0)) if not pd.isna(latest.get('BBU_20_2.0_2.0')) else None,
        bollinger_middle=float(latest.get('BBM_20_2.0_2.0', 0)) if not pd.isna(latest.get('BBM_20_2.0_2.0')) else None,
        bollinger_lower=float(latest.get('BBL_20_2.0_2.0', 0)) if not pd.isna(latest.get('BBL_20_2.0_2.0')) else None,
        atr_14=float(latest.get('ATRr_14', 0)) if not pd.isna(latest.get('ATRr_14')) else None,
        timestamp=str(latest.name)
    )

def calculate_support_resistance(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {}
    
    # Traditional Pivot Points based on previous day
    prev = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
    high = prev['High']
    low = prev['Low']
    close = prev['Close']
    
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    
    return {
        "pivot": pivot,
        "r1": r1,
        "r2": r2,
        "s1": s1,
        "s2": s2
    }

def get_indicator_overlay_data(df: pd.DataFrame) -> Dict[str, List[Dict]]:
    # Generate data structure suitable for lightweight-charts or similar charting libraries
    if df.empty:
        return {}
        
    df_clean = df.where(pd.notnull(df), None)
    
    def extract_series(col_name: str) -> List[Dict]:
        if col_name not in df_clean.columns:
            return []
        series = []
        for index, row in df_clean.iterrows():
            if row[col_name] is not None:
                series.append({
                    "time": str(index.date()) if hasattr(index, 'date') else str(index),
                    "value": row[col_name]
                })
        return series
        
    return {
        "sma_20": extract_series("SMA_20"),
        "sma_50": extract_series("SMA_50"),
        "sma_200": extract_series("SMA_200"),
        "bb_upper": extract_series("BBU_20_2.0_2.0"),
        "bb_middle": extract_series("BBM_20_2.0_2.0"),
        "bb_lower": extract_series("BBL_20_2.0_2.0"),
    }
