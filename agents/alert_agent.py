import pandas as pd
import os
from config import TICKERS, WEIGHTS, DATA_PATH, RISK_METRICS_PATH, ALERTS_PATH
import logging

logger = logging.getLogger(__name__ == "__main__")

class AlertAgent:
    def __init__(self):
        self.metrics_path = 'data/risk_metrics.csv'
        self.output_path = 'data/alerts.txt'
        self.very_high_risk = 5.0
        self.high_risk = 2.0

    def run(self):
        logging.info("📡 AlertAgent: Processing risk metrics...")

        alerts = []
        try:
            df = pd.read_csv(self.metrics_path)

            for _, row in df.iterrows():
                conf = int(row['confidence'] * 100)
                var_param = abs(row['parametric_VaR_1d'])
                var_hist = abs(row['historical_VaR_1d'])

                if var_param >= self.very_high_risk or var_hist >= self.very_high_risk:
                    alerts.append(
                        f"🚨 CRITICAL RISK: {conf}% VaR = {var_param:.2f}% or "
                        f"{var_hist:.2f}% daily loss likely"
                    )
                elif var_param >= self.high_risk or var_hist >= self.high_risk:
                    alerts.append(
                        f"⚠️ HIGH RISK: {conf}% VaR = {var_param:.2f}% or "
                        f"{var_hist:.2f}% daily loss likely"
                    )
        except FileNotFoundError:
            alerts = ["⚠️ WARN: No risk metrics found (run Data + Model agents first)"]
        except Exception as e:
            alerts = [f"❌ AlertAgent ERROR: {e}"]

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            if alerts:
                for alert in alerts:
                    f.write(alert + '\n')
            else:
                f.write("✅ All clear: Market Risk within tolerance\n")

        logging.info(f"✅ Alerts saved to {self.output_path}")
        return self.output_path