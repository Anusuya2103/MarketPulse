"""
Market Pulse — Yahoo Finance backend.

Yahoo Finance has no official API, so this uses `yfinance`, a free but
UNOFFICIAL library that reads Yahoo's own website endpoints. It can break
or get throttled without notice — that's the tradeoff for "free + no API
key" vs. Alpha Vantage's official-but-rate-limited free tier.

Run:
    pip install -r requirements.txt
    uvicorn server:app --reload
Then open http://127.0.0.1:8000 in your browser.
"""
from datetime import datetime, timezone

import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Market Pulse — Yahoo Finance backend")

WATCHLIST = [
    {"symbol": "NVDA", "yf": "NVDA",        "name": "NVIDIA Corp.",       "ccy": "$", "market": "US",  "sector": "AI / Semis"},
    {"symbol": "AAPL", "yf": "AAPL",        "name": "Apple Inc.",         "ccy": "$", "market": "US",  "sector": "Consumer Tech"},
    {"symbol": "MSFT", "yf": "MSFT",        "name": "Microsoft Corp.",    "ccy": "$", "market": "US",  "sector": "Cloud & Software"},
    {"symbol": "TSLA", "yf": "TSLA",        "name": "Tesla Inc.",         "ccy": "$", "market": "US",  "sector": "Auto & Energy"},
    {"symbol": "TCS",  "yf": "TCS.NS",      "name": "Tata Consultancy",   "ccy": "\u20b9", "market": "NSE", "sector": "IT Services"},
    {"symbol": "INFY", "yf": "INFY.NS",     "name": "Infosys Ltd.",       "ccy": "\u20b9", "market": "NSE", "sector": "IT Services"},
    {"symbol": "RELI", "yf": "RELIANCE.NS", "name": "Reliance Industries","ccy": "\u20b9", "market": "NSE", "sector": "Energy & Conglomerate"},
    {"symbol": "HDFB", "yf": "HDFCBANK.NS", "name": "HDFC Bank Ltd.",     "ccy": "\u20b9", "market": "NSE", "sector": "Banking & Finance"},
]
BY_SYMBOL = {s["symbol"]: s for s in WATCHLIST}


@app.get("/api/quotes")
def get_quotes():
    """Latest quote for every watchlist symbol, via yfinance's fast_info."""
    out = []
    for s in WATCHLIST:
        row = dict(s)
        try:
            fi = yf.Ticker(s["yf"]).fast_info
            price = fi["last_price"]
            prev = fi["previous_close"]
            change = price - prev if prev else 0
            change_pct = (change / prev * 100) if prev else 0
            row.update({
                "price": round(price, 2),
                "open": round(fi.get("open", price), 2),
                "high": round(fi.get("day_high", price), 2),
                "low": round(fi.get("day_low", price), 2),
                "volume": int(fi.get("last_volume") or 0),
                "change": round(change, 2),
                "changePercent": round(change_pct, 2),
                "error": None,
            })
        except Exception as e:  # yfinance / Yahoo hiccup — keep the row, flag it
            row.update({"price": None, "error": str(e)})
        out.append(row)
    return {"quotes": out, "asOf": datetime.now(timezone.utc).isoformat()}


@app.get("/api/history/{symbol}")
def get_history(symbol: str, days: int = 20):
    """Recent daily OHLCV for one watchlist symbol, via yfinance history()."""
    meta = BY_SYMBOL.get(symbol.upper())
    if not meta:
        raise HTTPException(404, f"Unknown symbol: {symbol}")
    try:
        hist = yf.Ticker(meta["yf"]).history(period="2mo")
    except Exception as e:
        raise HTTPException(502, f"Yahoo Finance fetch failed: {e}")
    hist = hist.tail(days)
    series = [
        {"date": idx.strftime("%Y-%m-%d"), "close": round(float(r["Close"]), 2), "volume": int(r["Volume"])}
        for idx, r in hist.iterrows()
    ]
    return {"symbol": symbol, "series": series, "asOf": datetime.now(timezone.utc).isoformat()}


# Serve the dashboard frontend (static/index.html) at "/".
# Declared last so it doesn't shadow the /api routes above.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
