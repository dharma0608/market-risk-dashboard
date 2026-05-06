from agents.data_agent import DataAgent
import os
import pandas as pd

def test_data_agent():
    da = DataAgent()
    data_path = da.run()
    assert os.path.exists(data_path), "Data file not created"
    df = pd.read_csv(data_path)
    assert not df.empty, "Data CSV is empty"

if __name__ == "__main__":
    test_data_agent()