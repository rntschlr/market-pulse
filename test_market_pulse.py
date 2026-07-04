#!/usr/bin/env python3
"""Unit tests for market_pulse CLI tool."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import json

# Import the module to test
import market_pulse


class TestFetchPrices(unittest.TestCase):
    """Test the fetch_prices function."""

    @patch('market_pulse.requests.get')
    def test_fetch_prices_success(self, mock_get):
        """Test successful API call to fetch prices."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'bitcoin': {'usd': 68421.50, 'usd_24h_change': 2.34},
            'ethereum': {'usd': 3812.45, 'usd_24h_change': -0.87}
        }
        mock_get.return_value = mock_response

        result = market_pulse.fetch_prices(['bitcoin', 'ethereum'], 'usd')

        self.assertIn('bitcoin', result)
        self.assertIn('ethereum', result)
        self.assertEqual(result['bitcoin']['usd'], 68421.50)
        self.assertEqual(result['bitcoin']['usd_24h_change'], 2.34)

    @patch('market_pulse.requests.get')
    def test_fetch_prices_timeout(self, mock_get):
        """Test timeout error handling."""
        mock_get.side_effect = market_pulse.requests.Timeout()

        with self.assertRaises(market_pulse.requests.Timeout):
            market_pulse.fetch_prices(['bitcoin'], 'usd')

    @patch('market_pulse.requests.get')
    def test_fetch_prices_http_error(self, mock_get):
        """Test HTTP error handling."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = market_pulse.requests.HTTPError()
        mock_get.return_value = mock_response

        with self.assertRaises(market_pulse.requests.HTTPError):
            market_pulse.fetch_prices(['bitcoin'], 'usd')

    @patch('market_pulse.requests.get')
    def test_fetch_prices_multiple_currencies(self, mock_get):
        """Test fetching prices in different currency."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'bitcoin': {'eur': 63000.00, 'eur_24h_change': 1.50}
        }
        mock_get.return_value = mock_response

        result = market_pulse.fetch_prices(['bitcoin'], 'eur')

        self.assertIn('bitcoin', result)
        self.assertEqual(result['bitcoin']['eur'], 63000.00)
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('eur', call_args[1]['params']['vs_currencies'])


class TestColorChange(unittest.TestCase):
    """Test the color_change formatting function."""

    def test_positive_change(self):
        """Test positive percentage formatting."""
        result = market_pulse.color_change(2.34)
        self.assertIn('+2.34%', result)
        self.assertIn(market_pulse.GREEN, result)

    def test_negative_change(self):
        """Test negative percentage formatting."""
        result = market_pulse.color_change(-0.87)
        self.assertIn('-0.87%', result)
        self.assertIn(market_pulse.RED, result)

    def test_zero_change(self):
        """Test zero percentage formatting."""
        result = market_pulse.color_change(0.0)
        self.assertIn('+0.00%', result)
        self.assertIn(market_pulse.GREEN, result)

    def test_large_positive_change(self):
        """Test large positive change."""
        result = market_pulse.color_change(123.456)
        self.assertIn('+123.46%', result)

    def test_large_negative_change(self):
        """Test large negative change."""
        result = market_pulse.color_change(-45.678)
        self.assertIn('-45.68%', result)


class TestDisplay(unittest.TestCase):
    """Test the display function output."""

    @patch('builtins.print')
    def test_display_basic(self, mock_print):
        """Test basic display output."""
        data = {
            'bitcoin': {'usd': 68421.50, 'usd_24h_change': 2.34},
            'ethereum': {'usd': 3812.45, 'usd_24h_change': -0.87}
        }

        market_pulse.display(data, 'usd')

        # Check that print was called
        self.assertGreater(mock_print.call_count, 0)

        # Verify key elements appear in output
        calls_str = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn('market-pulse', calls_str)
        self.assertIn('Bitcoin', calls_str)
        self.assertIn('Ethereum', calls_str)

    @patch('builtins.print')
    def test_display_price_formatting_large(self, mock_print):
        """Test price formatting for values >= 1."""
        data = {'bitcoin': {'usd': 68421.50, 'usd_24h_change': 0}}

        market_pulse.display(data, 'usd')

        calls_str = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn('$68,421.50', calls_str)

    @patch('builtins.print')
    def test_display_price_formatting_small(self, mock_print):
        """Test price formatting for values < 1."""
        data = {'dogecoin': {'usd': 0.082456, 'usd_24h_change': 0}}

        market_pulse.display(data, 'usd')

        calls_str = ''.join(str(call) for call in mock_print.call_args_list)
        # Should show 6 decimal places for small prices
        self.assertIn('0.082456', calls_str)

    @patch('builtins.print')
    def test_display_different_currency(self, mock_print):
        """Test display with different currency symbol."""
        data = {'bitcoin': {'eur': 63000.00, 'eur_24h_change': 0}}

        market_pulse.display(data, 'eur')

        calls_str = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn('EUR', calls_str)


class TestMain(unittest.TestCase):
    """Test main function and argument parsing."""

    @patch('market_pulse.display')
    @patch('market_pulse.fetch_prices')
    def test_main_default_coins(self, mock_fetch, mock_display):
        """Test main function with default coins."""
        mock_fetch.return_value = {
            'bitcoin': {'usd': 68421.50, 'usd_24h_change': 2.34}
        }

        with patch.object(sys, 'argv', ['market_pulse.py']):
            market_pulse.main()

        mock_fetch.assert_called_once()
        # Check that default coins are used
        call_args = mock_fetch.call_args[0][0]
        self.assertIn('bitcoin', call_args)

    @patch('market_pulse.display')
    @patch('market_pulse.fetch_prices')
    def test_main_custom_coins(self, mock_fetch, mock_display):
        """Test main function with custom coin selection."""
        mock_fetch.return_value = {
            'cardano': {'usd': 0.98, 'usd_24h_change': 1.5}
        }

        with patch.object(sys, 'argv', ['market_pulse.py', 'cardano']):
            market_pulse.main()

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0][0]
        self.assertIn('cardano', call_args)

    @patch('market_pulse.display')
    @patch('market_pulse.fetch_prices')
    def test_main_custom_currency(self, mock_fetch, mock_display):
        """Test main function with custom currency."""
        mock_fetch.return_value = {
            'bitcoin': {'eur': 63000.00, 'eur_24h_change': 1.5}
        }

        with patch.object(sys, 'argv', ['market_pulse.py', '--vs', 'eur']):
            market_pulse.main()

        mock_fetch.assert_called_once()
        # Check currency argument
        self.assertEqual(mock_fetch.call_args[0][1], 'eur')

    @patch('market_pulse.fetch_prices')
    def test_main_empty_response(self, mock_fetch):
        """Test main function handles empty API response."""
        mock_fetch.return_value = {}

        with patch.object(sys, 'argv', ['market_pulse.py']):
            with self.assertRaises(SystemExit):
                market_pulse.main()

    @patch('market_pulse.fetch_prices')
    def test_main_network_error(self, mock_fetch):
        """Test main function handles network errors gracefully."""
        mock_fetch.side_effect = market_pulse.requests.ConnectionError("Network error")

        with patch.object(sys, 'argv', ['market_pulse.py']):
            with self.assertRaises(SystemExit):
                market_pulse.main()


class TestColorConstants(unittest.TestCase):
    """Test that color constants are properly defined."""

    def test_color_constants_exist(self):
        """Test that all color constants are defined."""
        self.assertTrue(hasattr(market_pulse, 'RED'))
        self.assertTrue(hasattr(market_pulse, 'GREEN'))
        self.assertTrue(hasattr(market_pulse, 'YELLOW'))
        self.assertTrue(hasattr(market_pulse, 'CYAN'))
        self.assertTrue(hasattr(market_pulse, 'BOLD'))
        self.assertTrue(hasattr(market_pulse, 'DIM'))
        self.assertTrue(hasattr(market_pulse, 'RESET'))

    def test_color_constants_are_ansi(self):
        """Test that color constants are ANSI escape codes."""
        self.assertTrue(market_pulse.RED.startswith('\033['))
        self.assertTrue(market_pulse.RESET.endswith('m'))


if __name__ == '__main__':
    unittest.main()
