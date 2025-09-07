"""Application configuration and constants."""

from typing import Dict, Any

# Application Configuration
APP_CONFIG = {
    'page_title': "AI SA-CCR Platform",
    'page_icon': "🤖",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# LLM Default Configuration
DEFAULT_LLM_CONFIG = {
    'base_url': "http://localhost:8123/v1",
    'api_key': "dummy",
    'model': "llama3",
    'temperature': 0.3,
    'max_tokens': 4000,
    'streaming': False
}

# Currency and Asset Configuration
MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD", "SEK", "NOK"]
G10_CURRENCIES = MAJOR_CURRENCIES
EMERGING_CURRENCIES = ["CNY", "INR", "BRL", "MXN", "ZAR", "KRW", "TWD", "SGD"]

# Basel Regulatory Constants
BASEL_CAPITAL_RATIO = 0.08
BASEL_MINIMUM_MULTIPLIER = 0.05
BASEL_MULTIPLIER_PARAM = 0.95
BASEL_MULTIPLIER_DENOMINATOR = 0.05
