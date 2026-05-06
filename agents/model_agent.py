import pandas as pd
import numpy as np
from scipy.stats import norm
import os
from config import TICKERS, WEIGHTS, DATA_PATH, RISK_METRICS_PATH, ALERTS_PATH
import logging


logger = logging.getLogger(__name__ == "__main__")


class ModelAgent:
    def __init__(self):
        self.data_path = 'data/portfolio_data.csv'
        self.risk_metrics_path = 'data/risk_metrics.csv'
        self.confidences = [0.95, 0.99]

    def load_data(self):
        logging.info("📊 ModelAgent: Loading portfolio returns...")
        df = pd.read_csv(self.data_path, index_col='Date', parse_dates=True)
        return df['portfolio_returns'].dropna()

    def compute_parametric_var(self, returns, confidence):
        mean = returns.mean()
        std = returns.std()
        z = norm.ppf(confidence)
        VaR = mean - z * std
        return VaR

    def compute_historical_var(self, returns, confidence):
        alpha = 1 - confidence
        VaR = np.percentile(returns, 100 * alpha)
        return VaR

    def compute_cvar(self, returns, VaR):
        tail_losses = returns[returns <= VaR]
        if len(tail_losses) == 0:
            return np.nan
        return tail_losses.mean()

    def run(self):
        try:
            logging.info("📊 ModelAgent: Running risk model...")
            returns = self.load_data()
            if returns.empty:
                raise ValueError("No returns data")

            results = []
            for conf in self.confidences:
                parametric_VaR = self.compute_parametric_var(returns, conf)
                historical_VaR = self.compute_historical_var(returns, conf)
                parametric_CVaR = self.compute_cvar(returns, parametric_VaR)
                historical_CVaR = self.compute_cvar(returns, historical_VaR)

                results.append({
                    'confidence': conf,
                    'parametric_VaR_1d': parametric_VaR * 100,
                    'historical_VaR_1d': historical_VaR * 100,
                    'parametric_CVaR_1d': parametric_CVaR * 100,
                    'historical_CVaR_1d': historical_CVaR * 100,
                })

            metrics_df = pd.DataFrame(results).round(3)
            os.makedirs(os.path.dirname(self.risk_metrics_path), exist_ok=True)
            metrics_df.to_csv(self.risk_metrics_path, index=False)
            logging.info(f"✅ ModelAgent: Saved risk metrics to {self.risk_metrics_path}")
            return self.risk_metrics_path
        except Exception as e:
            logging.error(f"❌ ModelAgent FAILED: {e}")
            return None