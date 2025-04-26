# Deriv Index Tick Data Fetcher

A Python application that continuously fetches tick data from Deriv's API for Volatility 10, 75, and 100 Indexes (R_10, R_75, R_100).

## Features

- Connects to Deriv's WebSocket API
- Fetches data in 5,000-tick batches (Deriv's API limit)
- Uses timestamp-based incremental fetching to ensure no gaps or overlaps
- Automatically schedules fetch cycles
- Stores tick data in organized CSV files
- Optimized for AI/ML training data collection

## Project Structure

```
/
├── config.py               # Configuration settings
├── deriv_api.py            # Deriv API connection handler
├── data_fetcher.py         # Main data fetching logic
├── data_storage.py         # Data storage utilities
├── scheduler.py            # Scheduling functionality
├── main.py                 # Application entry point
├── .env                    # Environment variables (API token)
├── requirements.txt        # Dependencies
└── data/                   # Data storage directory
    ├── R_10/               # R_10 tick data
    ├── R_75/               # R_75 tick data
    └── R_100/              # R_100 tick data
```

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Deriv API token:
   ```
   DERIV_API_TOKEN=your_api_token_here
   ```

## Usage

Run the application:

```
python main.py
```

The application will start fetching tick data for the configured symbols and store it in the data directory.

## Configuration

Edit `config.py` to customize:
- Symbols to fetch
- Fetch interval
- Storage paths
- Logging settings
