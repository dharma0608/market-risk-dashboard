import yfinance as yf
import pandas as pd
import numpy as np
import os
from config import TICKERS, WEIGHTS, DATA_PATH, RISK_METRICS_PATH, ALERTS_PATH
import logging


logger = logging.getLogger(__name__ == "__main__")


class DataAgent:
    def __init__(self):
        self.tickers = ['AAPL', 'TSLA', 'SPY', 'GLD']
        self.weights = [0.4, 0.3, 0.2, 0.1]  # Portfolio weights
        self.data_path = 'data/portfolio_data.csv'

    def run(self):
        """Fetch data, compute returns, save CSV"""
        try:
            logging.info("📊 DataAgent: Fetching market data...")

            # Download 1 year daily data, multi-index columns
            raw_data = yf.download(
                self.tickers,
                period='1y',
                progress=False,
                auto_adjust=False
            )

            if raw_data.empty:
                raise ValueError("No data returned from yfinance")

            # Extract Close prices
            close_data = raw_data.loc[:, 'Close']
            close_data.columns = self.tickers

            # Compute log returns
            returns = np.log(close_data / close_data.shift(1)).dropna()

            # Portfolio returns (weighted)
            port_returns = (returns * self.weights).sum(axis=1)

            # Rolling volatility (20‑day annualized)
            port_returns_df = pd.DataFrame({'portfolio_returns': port_returns})
            port_returns_df['vol_20d'] = (
                port_returns.rolling(20).std() * np.sqrt(252)
            )

            # Save
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            port_returns_df.to_csv(self.data_path)

            logging.info(f"✅ DataAgent: Saved {len(port_returns_df)} days to {self.data_path}")
            return self.data_path

        except Exception as e:
            logging.error(f"❌ DataAgent FAILED: {e}")
            return None