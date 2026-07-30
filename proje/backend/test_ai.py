import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from app.services.ai_analyzer import AIAnalyzer
from app.services.data_fetcher import get_data_fetcher
from app.services.indicator_engine import calculate_indicators

async def main():
    print("=" * 60)
    print("3 Ajanli AI Analiz Testi - THYAO")
    print("=" * 60)

    fetcher = get_data_fetcher("yfinance")
    print("[1/3] THYAO verisi cekiliyor...")
    df = await fetcher.fetch_stock_data("THYAO", period="1y", interval="1d")
    indicators = calculate_indicators(df, "THYAO")
    print(f"      Fiyat: {indicators.last_price} TL | RSI: {indicators.rsi_14:.2f}")

    print("[2/3] Hisse bilgisi aliniyor...")
    stock_info = await fetcher.fetch_stock_info("THYAO")
    print(f"      Sirket: {stock_info.get('name', 'N/A')}")

    print("[3/3] 3 Ajanli Gemini analizi basliyor...")
    analyzer = AIAnalyzer()
    print(f"      Model: {analyzer.model_name}")
    
    result = await analyzer.run_full_analysis("THYAO", indicators, stock_info)
    
    print("\n" + "=" * 60)
    print("SONUCLAR")
    print("=" * 60)
    print(f"Teknik Analist  : {result.technical_analysis.signal} (%{result.technical_analysis.confidence*100:.0f} guven)")
    print(f"  {result.technical_analysis.analysis_text[:100]}")
    print(f"Temel Analist   : {result.fundamental_analysis.signal} (%{result.fundamental_analysis.confidence*100:.0f} guven)")
    print(f"  {result.fundamental_analysis.analysis_text[:100]}")
    print(f"Risk Yoneticisi : {result.risk_assessment.signal} (%{result.risk_assessment.confidence*100:.0f} guven)")
    print(f"FINAL KARAR     : {result.final_decision} (%{result.final_confidence*100:.0f} guven)")
    print(f"OZET: {result.summary[:200]}")
    print("=" * 60)

asyncio.run(main())
