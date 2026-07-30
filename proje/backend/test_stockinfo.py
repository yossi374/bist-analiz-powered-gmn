import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from app.services.data_fetcher import get_data_fetcher

async def main():
    fetcher = get_data_fetcher("yfinance")
    info = await fetcher.fetch_stock_info("THYAO")
    print("Stock info dondu:")
    for k, v in info.items():
        print(f"  {k}: {v}")

asyncio.run(main())
