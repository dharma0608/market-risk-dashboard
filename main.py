from agents.data_agent import DataAgent
from agents.model_agent import ModelAgent
from agents.alert_agent import AlertAgent
import os
from logging_config import configure_logging

configure_logging()
def run_pipeline():
    print("🚀 Starting Market Risk Agent Pipeline...")

    data_agent = DataAgent()
    data_path = data_agent.run()
    if not data_path or not os.path.exists(data_path):
        print("❌ Data Agent failed; stopping pipeline.")
        return

    model_agent = ModelAgent()
    metrics_path = model_agent.run()
    if not metrics_path or not os.path.exists(metrics_path):
        print("❌ Model Agent failed; stopping pipeline.")
        return

    alert_agent = AlertAgent()
    alert_path = alert_agent.run()
    print(f"✅ Pipeline complete: Alerts at {alert_path}")


if __name__ == "__main__":
    run_pipeline()