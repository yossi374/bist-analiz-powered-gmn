import urllib.request
import json
import sys

# Windows CP1254 encoding sorununu asla yasamayalim
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"

def get(path):
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=25) as r:
            data = json.loads(r.read())
        return data, None
    except Exception as e:
        return None, str(e)

print("=" * 60)
print("BIST Finansal Analiz Motoru - API Test")
print("=" * 60)

# 1. Root
data, err = get("/")
if err:
    print(f"[FAIL] GET /  -->  {err}")
else:
    print(f"[OK]   GET /  -->  {data['status']} | v{data['version']}")

# 2. Stock indicators (THYAO)
data, err = get("/api/v1/market/stock/THYAO")
if err:
    print(f"[FAIL] GET /market/stock/THYAO  -->  {err}")
else:
    bb_ok = data.get("bollinger_upper") is not None
    rsi   = data.get('rsi_14') or 0
    sma200= data.get('sma_200') or 0
    chg   = data.get('change_percent') or 0
    print(f"[OK]   GET /market/stock/THYAO")
    print(f"       Fiyat: {data.get('last_price')} TL")
    print(f"       RSI(14): {rsi:.2f}  |  SMA200: {sma200:.2f}  |  Degisim: %{chg:.2f}")
    print(f"       Bollinger: {'DOLU' if bb_ok else 'NULL - sorun var!'}")

# 3. Quick analysis
data, err = get("/api/v1/analysis/quick/THYAO")
if err:
    print(f"[FAIL] GET /analysis/quick/THYAO  -->  {err}")
else:
    print(f"[OK]   GET /analysis/quick/THYAO")
    print(f"       Sinyal: {data.get('quick_signal')}  |  Trend: {data.get('trend')}")
    print(f"       Ozet: {data.get('summary', '')[:120]}")

# 4. Indices
data, err = get("/api/v1/market/indices")
if err:
    print(f"[FAIL] GET /market/indices  -->  {err}")
else:
    print(f"[OK]   GET /market/indices  -->  {len(data)} endeks")
    for idx in data:
        sym = idx.get('symbol', '?')
        price = idx.get('last_price', 0) or 0
        chg   = idx.get('change_percent', 0) or 0
        print(f"       {sym:15s} | {price:.2f} | %{chg:.2f}")

print("=" * 60)
print("Swagger UI: http://localhost:8000/docs")
print("=" * 60)
