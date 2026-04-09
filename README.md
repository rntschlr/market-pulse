# market-pulse

Real-time stock and crypto prices in your terminal with color-coded 24h changes.

![Python](https://img.shields.io/badge/python-3.10+-blue)

## Quick Start

```bash
pip install -r requirements.txt
python market_pulse.py
```

## Usage

```bash
# Default coins (Bitcoin, Ethereum, Solana)
python market_pulse.py

# Specific coins
python market_pulse.py bitcoin dogecoin cardano

# Different quote currency
python market_pulse.py --vs eur
```

## Output

```
  market-pulse — live crypto prices

  Asset              Price       24h
  ────────────────────────────────────────
  Bitcoin        $68,421.00   +2.34%
  Ethereum        $3,812.50   -0.87%
  Solana            $142.30   +5.12%
```

## Data Source

Prices from [CoinGecko](https://www.coingecko.com/en/api) free API. No API key required.

## License

MIT
