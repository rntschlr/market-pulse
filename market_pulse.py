#!/usr/bin/env python3
"""market-pulse: Real-time stock and crypto prices in your terminal."""

import argparse
import sys

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests")
    sys.exit(1)

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

DEFAULT_CRYPTO = ["bitcoin", "ethereum", "solana"]
DEFAULT_CURRENCIES = ["usd"]

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def fetch_prices(coins: list[str], vs: str = "usd") -> dict:
    """Fetch current prices and 24h change from CoinGecko (free, no key)."""
    params = {
        "ids": ",".join(coins),
        "vs_currencies": vs,
        "include_24hr_change": "true",
    }
    resp = requests.get(COINGECKO_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def color_change(pct: float) -> str:
    """Color-code a percentage change."""
    sign = "+" if pct >= 0 else ""
    color = GREEN if pct >= 0 else RED
    return f"{color}{sign}{pct:.2f}%{RESET}"


def display(data: dict, vs: str = "usd") -> None:
    """Print prices with color-coded changes."""
    symbol = "$" if vs == "usd" else vs.upper() + " "

    print(f"\n{BOLD}{CYAN}  market-pulse{RESET} {DIM}— live crypto prices{RESET}\n")
    print(f"  {'Asset':<14} {'Price':>12}   {'24h':>10}")
    print(f"  {DIM}{'─' * 40}{RESET}")

    for coin, info in sorted(data.items()):
        price = info.get(vs, 0)
        change = info.get(f"{vs}_24h_change", 0) or 0

        if price >= 1:
            price_str = f"{symbol}{price:,.2f}"
        else:
            price_str = f"{symbol}{price:.6f}"

        change_str = color_change(change)
        name = coin.replace("-", " ").title()

        print(f"  {YELLOW}{name:<14}{RESET} {price_str:>12}   {change_str:>20}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch live crypto prices from CoinGecko"
    )
    parser.add_argument(
        "coins",
        nargs="*",
        default=DEFAULT_CRYPTO,
        help="Coin IDs (default: bitcoin ethereum solana)",
    )
    parser.add_argument(
        "--vs",
        default="usd",
        help="Quote currency (default: usd)",
    )
    args = parser.parse_args()

    try:
        data = fetch_prices(args.coins, args.vs)
        if not data:
            print(f"{RED}No data returned. Check coin IDs.{RESET}")
            sys.exit(1)
        display(data, args.vs)
    except requests.RequestException as e:
        print(f"{RED}Network error: {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
