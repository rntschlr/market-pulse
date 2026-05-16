#!/usr/bin/env python3
"""market-pulse: real-time crypto prices in your terminal."""

import argparse
from collections.abc import Sequence
import sys
from typing import Any

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests")
    sys.exit(1)

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

DEFAULT_CRYPTO = ["bitcoin", "ethereum", "solana"]

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def normalize_coin_ids(coins: Sequence[str]) -> list[str]:
    """Return unique, non-empty CoinGecko IDs in request order."""
    normalized: list[str] = []
    seen: set[str] = set()

    for coin in coins:
        value = coin.strip().lower()
        if value and value not in seen:
            normalized.append(value)
            seen.add(value)

    return normalized


def fetch_prices(coins: Sequence[str], vs: str = "usd") -> dict[str, dict[str, Any]]:
    """Fetch current prices and 24h change from CoinGecko (free, no key)."""
    normalized_coins = normalize_coin_ids(coins)
    if not normalized_coins:
        raise ValueError("At least one coin ID is required.")

    params = {
        "ids": ",".join(normalized_coins),
        "vs_currencies": vs,
        "include_24hr_change": "true",
    }
    resp = requests.get(COINGECKO_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def format_price(price: float, vs: str) -> str:
    """Format a crypto price for terminal display."""
    symbol = "$" if vs == "usd" else vs.upper() + " "
    return f"{symbol}{price:,.2f}" if price >= 1 else f"{symbol}{price:.6f}"


def color_change(pct: float) -> str:
    """Color-code a percentage change."""
    sign = "+" if pct >= 0 else ""
    color = GREEN if pct >= 0 else RED
    return f"{color}{sign}{pct:.2f}%{RESET}"


def display(data: dict[str, dict[str, Any]], vs: str = "usd") -> None:
    """Print prices with color-coded changes."""
    print(f"\n{BOLD}{CYAN}  market-pulse{RESET} {DIM}— live crypto prices{RESET}\n")
    print(f"  {'Asset':<14} {'Price':>12}   {'24h':>10}")
    print(f"  {DIM}{'─' * 40}{RESET}")

    for coin, info in sorted(data.items()):
        price = float(info.get(vs, 0) or 0)
        change = float(info.get(f"{vs}_24h_change", 0) or 0)
        price_str = format_price(price, vs)
        name = coin.replace("-", " ").title()

        print(f"  {YELLOW}{name:<14}{RESET} {price_str:>12}   {color_change(change):>20}")

    print()


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
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
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    coins = normalize_coin_ids(args.coins)
    vs = args.vs.strip().lower()

    if not coins:
        print(f"{RED}At least one coin ID is required.{RESET}", file=sys.stderr)
        return 2
    if not vs:
        print(f"{RED}Quote currency is required.{RESET}", file=sys.stderr)
        return 2

    try:
        data = fetch_prices(coins, vs)
        if not data:
            print(f"{RED}No data returned. Check coin IDs.{RESET}", file=sys.stderr)
            return 1
        display(data, vs)
        return 0
    except ValueError as e:
        print(f"{RED}{e}{RESET}", file=sys.stderr)
        return 2
    except requests.RequestException as e:
        print(f"{RED}Network error: {e}{RESET}", file=sys.stderr)
        return 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
