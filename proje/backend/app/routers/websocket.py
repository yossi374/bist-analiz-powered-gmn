from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import yfinance as yf
from datetime import datetime

router = APIRouter()

@router.websocket("/ws/ticker/{symbol}")
async def websocket_ticker(websocket: WebSocket, symbol: str):
    await websocket.accept()
    
    formatted_symbol = symbol.upper().strip()
    if not formatted_symbol.endswith(".IS"):
        formatted_symbol += ".IS"
        
    ticker = yf.Ticker(formatted_symbol)
    
    try:
        while True:
            try:
                # fast_info bir nesne — .get() değil doğrudan attribute ile eriş
                info = await asyncio.to_thread(lambda: ticker.fast_info)
                
                last_price    = getattr(info, 'last_price', 0) or 0
                prev_close    = getattr(info, 'previous_close', last_price) or last_price
                day_high      = getattr(info, 'day_high', 0) or 0
                day_low       = getattr(info, 'day_low', 0) or 0
                last_volume   = getattr(info, 'last_volume', 0) or 0
                change_pct    = ((last_price - prev_close) / prev_close * 100) if prev_close else 0.0
                
                message = {
                    "symbol": symbol,
                    "price": round(last_price, 2),
                    "high": round(day_high, 2),
                    "low": round(day_low, 2),
                    "volume": last_volume,
                    "change_percent": round(change_pct, 4),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(message)
            except Exception as inner_e:
                print(f"WS data error for {symbol}: {inner_e}")
                
            await asyncio.sleep(10)
            
    except WebSocketDisconnect:
        print(f"Client disconnected from ticker {symbol}")
    except Exception as e:
        print(f"Websocket error for {symbol}: {e}")
        try:
            await websocket.close()
        except:
            pass
