# Market Pulse — Yahoo Finance (local) edition

Real quotes and daily history from Yahoo Finance, via the free but **unofficial**
`yfinance` library. Yahoo has no official API — this reads the same internal
endpoints Yahoo's own website uses, which is why it has to run on your own
machine rather than as a hosted claude.ai page (that page's browser sandbox
can't call Yahoo's endpoints directly).

## Setup

```bash
cd market-pulse-yahoo
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload
```

Then open **http://127.0.0.1:8000** in your browser.

## What you get

- `GET /api/quotes` — current price, open/high/low, volume and % change for
  all 8 watchlist symbols (NVDA, AAPL, MSFT, TSLA, TCS, INFY, RELIANCE, HDFCBANK)
- `GET /api/history/{symbol}?days=20` — recent daily OHLCV
- A dashboard frontend (`static/index.html`) that polls those endpoints and
  renders the same KPI / chart / table layout as the Alpha Vantage version,
  with auto-refresh (default every 30s — adjustable in the top bar)

## Editing the watchlist

Edit the `WATCHLIST` list at the top of `server.py`. Use Yahoo's own ticker
format: US tickers as-is (`AAPL`), NSE tickers with a `.NS` suffix
(`RELIANCE.NS`), BSE with `.BO`.

## Known limitations

- **Unofficial**: Yahoo can change or block these endpoints without notice.
  If quotes stop working, check the [yfinance GitHub issues](https://github.com/ranaroussi/yfinance/issues)
  for reports of breakage before assuming your setup is wrong.
- **Rate limits**: Yahoo throttles aggressive polling. 30–60 second refresh
  for 8 symbols is normally fine; going much faster risks a temporary IP block.
- **Personal use only**: per Yahoo's Terms of Service, this data isn't
  licensed for commercial redistribution.
- This is a separate, self-hosted project from the Alpha Vantage version
  published as a claude.ai Artifact — they don't share code or state.
# MarketPulse
