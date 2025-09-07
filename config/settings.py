# ==============================================================================
# CONFIG/SETTINGS.PY - Application Configuration
# ==============================================================================

"""
Application configuration and constants for the SA-CCR platform.
Contains all configurable parameters, default values, and environment settings.
"""

import os
from typing import Dict, List, Any
from pathlib import Path

# ==============================================================================
# APPLICATION METADATA
# ==============================================================================

APP_NAME = "AI SA-CCR Platform"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Complete 24-Step Basel SA-CCR Calculator with LLM Integration"
APP_AUTHOR = "SA-CCR Development Team"

# ==============================================================================
# STREAMLIT CONFIGURATION
# ==============================================================================

STREAMLIT_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'Get Help': 'https://www.bis.org/bcbs/publ/bcbs279.htm',
        'Report a bug': None,
        'About': f"{APP_NAME} v{APP_VERSION} - {APP_DESCRIPTION}"
    }
}

# ==============================================================================
# LLM CONFIGURATION
# ==============================================================================

# Default LLM Configuration
DEFAULT_LLM_CONFIG = {
    'base_url': os.getenv('LLM_BASE_URL', "http://localhost:8123/v1"),
    'api_key': os.getenv('LLM_API_KEY', "dummy"),
    'model': os.getenv('LLM_MODEL', "llama3"),
    'temperature': float(os.getenv('LLM_TEMPERATURE', '0.3')),
    'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '4000')),
    'streaming': os.getenv('LLM_STREAMING', 'false').lower() == 'true',
    'timeout': int(os.getenv('LLM_TIMEOUT', '30'))  # seconds
}

# LLM Model Options
SUPPORTED_LLM_MODELS = [
    "llama3",
    "llama3-70b",
    "gpt-3.5-turbo",
    "gpt-4",
    "claude-3-sonnet",
    "claude-3-opus",
    "mistral-7b",
    "mixtral-8x7b"
]

# LLM Temperature Ranges
LLM_TEMPERATURE_RANGE = {
    'min': 0.0,
    'max': 1.0,
    'default': 0.3,
    'step': 0.1
}

# LLM Token Limits
LLM_TOKEN_LIMITS = {
    'min': 500,
    'max': 8000,
    'default': 4000,
    'step': 100
}

# ==============================================================================
# CURRENCY AND MARKET CONFIGURATION
# ==============================================================================

# Major Currencies
MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD"]

# G10 Currencies (for supervisory factor determination)
G10_CURRENCIES = [
    "USD", "EUR", "JPY", "GBP", "CHF", 
    "CAD", "AUD", "NZD", "SEK", "NOK"
]

# Emerging Market Currencies
EMERGING_CURRENCIES = [
    "CNY", "INR", "BRL", "MXN", "ZAR", 
    "KRW", "TWD", "SGD", "HKD", "THB"
]

# All Supported Currencies
ALL_CURRENCIES = MAJOR_CURRENCIES + EMERGING_CURRENCIES

# Currency Display Names
CURRENCY_DISPLAY_NAMES = {
    "USD": "US Dollar",
    "EUR": "Euro", 
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "CHF": "Swiss Franc",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "NZD": "New Zealand Dollar",
    "SEK": "Swedish Krona",
    "NOK": "Norwegian Krone",
    "CNY": "Chinese Yuan",
    "INR": "Indian Rupee",
    "BRL": "Brazilian Real",
    "MXN": "Mexican Peso",
    "ZAR": "South African Rand",
    "KRW": "South Korean Won",
    "TWD": "Taiwan Dollar",
    "SGD": "Singapore Dollar",
    "HKD": "Hong Kong Dollar",
    "THB": "Thai Baht"
}

# ==============================================================================
# BASEL REGULATORY CONSTANTS
# ==============================================================================

# Core Basel Parameters
BASEL_CAPITAL_RATIO = 0.08  # 8% minimum capital ratio
BASEL_ALPHA = 1.4  # SA-CCR alpha multiplier
BASEL_MIN_MULTIPLIER = 0.05  # Minimum PFE multiplier
BASEL_MULTIPLIER_SCALING = 0.95  # PFE multiplier scaling factor

# Maturity Buckets for Interest Rate Trades
IR_MATURITY_BUCKETS = {
    'short': {'label': '<2y', 'max_years': 2},
    'medium': {'label': '2-5y', 'max_years': 5},
    'long': {'label': '>5y', 'max_years': float('inf')}
}

# Default Assumptions for Missing Data
DEFAULT_ASSUMPTIONS = {
    'option_delta': 1.0,
    'mtm_value': 0.0,
    'threshold': 0.0,
    'mta': 0.0,
    'nica': 0.0,
    'ceu_flag': 1,  # Non-centrally cleared
    'basis_flag': False,
    'volatility_flag': False
}

# ==============================================================================
# DATA VALIDATION SETTINGS
# ==============================================================================

# Input Validation Limits
VALIDATION_LIMITS = {
    'max_notional': 1e12,  # $1 trillion
    'min_notional': 1000,  # $1,000
    'max_trades_per_netting_set': 1000,
    'max_maturity_years': 50,
    'min_maturity_days': 1,
    'max_threshold': 1e10,  # $10 billion
    'max_mta': 1e9,  # $1 billion
    'max_collateral_amount': 1e11  # $100 billion
}

# Data Quality Thresholds
DATA_QUALITY_THRESHOLDS = {
    'high_impact_threshold': 0.1,  # 10% of portfolio
    'medium_impact_threshold': 0.05,  # 5% of portfolio
    'missing_data_warning_pct': 0.2,  # 20% missing data
    'stale_data_days': 5,  # Data older than 5 days
    'mtm_threshold': 1000  # Minimum MTM to consider significant
}

# ==============================================================================
# UI CONFIGURATION
# ==============================================================================

# Page Configuration
PAGE_CONFIG = {
    'calculator': {
        'title': "SA-CCR Calculator",
        'icon': "🧮",
        'description': "Complete 24-step Basel regulatory calculation"
    },
    'reference': {
        'title': "Reference Example",
        'icon': "📋", 
        'description': "Lowell Hotel Properties LLC case study"
    },
    'ai_assistant': {
        'title': "AI Assistant",
        'icon': "🤖",
        'description': "Interactive SA-CCR expert guidance"
    },
    'portfolio': {
        'title': "Portfolio Analysis",
        'icon': "📊",
        'description': "Portfolio optimization and insights"
    }
}

# Chart Configuration
CHART_CONFIG = {
    'default_theme': 'plotly_white',
    'color_palette': [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
    ],
    'figure_height': 400,
    'figure_width': 600
}

# Table Configuration
TABLE_CONFIG = {
    'max_rows_display': 100,
    'decimal_places': 2,
    'currency_format': "${:,.0f}",
    'percentage_format': "{:.2%}",
    'large_number_format': "${:,.1f}M"
}

# ==============================================================================
# CALCULATION SETTINGS
# ==============================================================================

# Calculation Performance Settings
CALCULATION_CONFIG = {
    'enable_caching': True,
    'cache_duration_minutes': 30,
    'parallel_processing': False,  # Set to True for large portfolios
    'batch_size': 100,  # For batch processing
    'progress_update_interval': 10  # Steps between progress updates
}

# Thinking Process Settings
THINKING_PROCESS_CONFIG = {
    'enable_detailed_thinking': True,
    'enable_step_reasoning': True,
    'enable_formula_breakdown': True,
    'thinking_detail_level': 'detailed',  # 'basic', 'detailed', 'verbose'
    'max_thinking_length': 5000  # characters
}

# ==============================================================================
# EXPORT SETTINGS
# ==============================================================================

# Export Configuration
EXPORT_CONFIG = {
    'csv_encoding': 'utf-8',
    'excel_engine': 'openpyxl',
    'json_indent': 2,
    'include_metadata': True,
    'include_thinking_steps': True,
    'compress_large_exports': True,
    'max_export_size_mb': 50
}

# File Naming Conventions
FILE_NAMING = {
    'timestamp_format': '%Y%m%d_%H%M%S',
    'summary_prefix': 'saccr_summary',
    'steps_prefix': 'saccr_steps',
    'full_prefix': 'saccr_full',
    'portfolio_prefix': 'portfolio_analysis'
}

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

# Logging Settings
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': 'logs/saccr_app.log',
    'max_file_size_mb': 10,
    'backup_count': 5,
    'enable_console_logging': True,
    'enable_file_logging': True
}

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

# Security Configuration
SECURITY_CONFIG = {
    'enable_input_sanitization': True,
    'max_upload_size_mb': 10,
    'allowed_file_types': ['.csv', '.xlsx', '.json'],
    'session_timeout_minutes': 120,
    'enable_rate_limiting': False,  # Enable for production
    'max_requests_per_minute': 60
}

# ==============================================================================
# DEVELOPMENT SETTINGS
# ==============================================================================

# Development Configuration
DEV_CONFIG = {
    'debug_mode': os.getenv('DEBUG', 'false').lower() == 'true',
    'enable_profiling': False,
    'show_debug_info': False,
    'enable_test_data': True,
    'mock_llm_responses': False,
    'enable_experimental_features': False
}

# Test Data Settings
TEST_DATA_CONFIG = {
    'enable_sample_trades': True,
    'sample_portfolio_size': 5,
    'use_realistic_values': True,
    'include_edge_cases': False
}

# ==============================================================================
# ENVIRONMENT-SPECIFIC SETTINGS
# ==============================================================================

def get_environment():
    """Determine current environment."""
    return os.getenv('ENVIRONMENT', 'development').lower()

def is_production():
    """Check if running in production."""
    return get_environment() == 'production'

def is_development():
    """Check if running in development."""
    return get_environment() == 'development'

# Environment-specific configurations
ENVIRONMENT_CONFIGS = {
    'development': {
        'enable_debug_features': True,
        'cache_calculations': False,
        'show_performance_metrics': True,
        'enable_hot_reload': True
    },
    'staging': {
        'enable_debug_features': False,
        'cache_calculations': True,
        'show_performance_metrics': False,
        'enable_hot_reload': False
    },
    'production': {
        'enable_debug_features': False,
        'cache_calculations': True,
        'show_performance_metrics': False,
        'enable_hot_reload': False,
        'optimize_performance': True,
        'enable_monitoring': True
    }
}

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value with environment variable override."""
    env_key = key.upper().replace('.', '_')
    return os.getenv(env_key, default)

def get_environment_config() -> Dict[str, Any]:
    """Get configuration for current environment."""
    env = get_environment()
    return ENVIRONMENT_CONFIGS.get(env, ENVIRONMENT_CONFIGS['development'])

def validate_config() -> List[str]:
    """Validate configuration settings and return any issues."""
    issues = []
    
    # Validate LLM configuration
    if not DEFAULT_LLM_CONFIG['base_url']:
        issues.append("LLM base URL not configured")
    
    # Validate file paths
    log_dir = Path(LOGGING_CONFIG['file_path']).parent
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create log directory: {e}")
    
    # Validate limits
    if VALIDATION_LIMITS['max_notional'] <= VALIDATION_LIMITS['min_notional']:
        issues.append("Invalid notional limits configuration")
    
    return issues

def get_display_config() -> Dict[str, Any]:
    """Get configuration optimized for display."""
    return {
        'app_info': {
            'name': APP_NAME,
            'version': APP_VERSION,
            'description': APP_DESCRIPTION
        },
        'supported_currencies': len(ALL_CURRENCIES),
        'supported_models': len(SUPPORTED_LLM_MODELS),
        'environment': get_environment(),
        'debug_mode': DEV_CONFIG['debug_mode']
    }

# ==============================================================================
# CONFIGURATION CONSTANTS FOR EXTERNAL USE
# ==============================================================================

# Export commonly used configurations
__all__ = [
    'STREAMLIT_CONFIG',
    'DEFAULT_LLM_CONFIG', 
    'MAJOR_CURRENCIES',
    'G10_CURRENCIES',
    'BASEL_CAPITAL_RATIO',
    'BASEL_ALPHA',
    'VALIDATION_LIMITS',
    'PAGE_CONFIG',
    'CHART_CONFIG',
    'TABLE_CONFIG',
    'get_environment_config',
    'is_production',
    'is_development'
]
