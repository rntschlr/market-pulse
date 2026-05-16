from unittest.mock import Mock, patch

import requests

import market_pulse


def test_normalize_coin_ids_strips_deduplicates_and_preserves_order():
    assert market_pulse.normalize_coin_ids([" Bitcoin ", "ethereum", "bitcoin", ""]) == [
        "bitcoin",
        "ethereum",
    ]


def test_fetch_prices_calls_coingecko_with_normalized_params():
    response = Mock()
    response.json.return_value = {"bitcoin": {"usd": 123.45}}

    with patch("market_pulse.requests.get", return_value=response) as get:
        data = market_pulse.fetch_prices([" Bitcoin ", "bitcoin"], "usd")

    assert data == {"bitcoin": {"usd": 123.45}}
    response.raise_for_status.assert_called_once_with()
    get.assert_called_once_with(
        market_pulse.COINGECKO_URL,
        params={
            "ids": "bitcoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        },
        timeout=10,
    )


def test_format_price_uses_decimal_precision_for_sub_unit_values():
    assert market_pulse.format_price(0.1234567, "usd") == "$0.123457"
    assert market_pulse.format_price(1234.5, "eur") == "EUR 1,234.50"


def test_run_returns_error_code_when_request_fails(capsys):
    with patch(
        "market_pulse.fetch_prices",
        side_effect=requests.Timeout("request timed out"),
    ):
        assert market_pulse.run(["bitcoin"]) == 1

    captured = capsys.readouterr()
    assert "Network error" in captured.err


def test_run_displays_data_for_valid_response(capsys):
    with patch(
        "market_pulse.fetch_prices",
        return_value={"bitcoin": {"usd": 100, "usd_24h_change": 1.25}},
    ):
        assert market_pulse.run(["bitcoin"]) == 0

    captured = capsys.readouterr()
    assert "Bitcoin" in captured.out
    assert "$100.00" in captured.out
