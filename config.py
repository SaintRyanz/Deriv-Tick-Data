"""
Configuration settings for the Deriv Index Tick Data Fetcher application.
"""
import os
from datetime import datetime
import pytz

# API Configuration
DERIV_API_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

# Symbols to fetch
SYMBOLS = ["R_10", "R_75", "R_100"]

# Fetch Configuration
TICKS_PER_FETCH = 5000  # Maximum allowed by Deriv API
FETCH_INTERVAL_SECONDS = 10000  # ~2 hours 47 minutes

# Storage Configuration
BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Ensure data directories exist
for symbol in SYMBOLS:
    os.makedirs(os.path.join(BASE_DATA_DIR, symbol), exist_ok=True)

# Get current date in UTC
def get_current_date_str():
    """Get current date in YYYY-MM-DD format (UTC)"""
    return datetime.now(pytz.UTC).strftime("%Y-%m-%d")

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tick_fetcher.log")

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5
