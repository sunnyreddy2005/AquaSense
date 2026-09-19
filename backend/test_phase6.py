import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import json
from app.agents.data_agent import DataAgent
from app.agents.anomaly_agent import AnomalyAgent

def main():
    print("Loading and cleaning data...")
    data_agent = DataAgent()
    # Using the raw dataset to let the data agent clean it first
    df_clean, profile, _ = data_agent.process_dataset("data/raw/water_consumption.csv")
    
    timestamp_col = profile['timestamp_column']
    consumption_col = profile['consumption_column']
    
    print("\nInitializing Anomaly Agent...")
    anomaly_agent = AnomalyAgent()
    
    print("\nDetecting anomalies...")
    result = anomaly_agent.detect_anomalies(df_clean, timestamp_col, consumption_col)
    
    print(f"\nTotal Anomalies Detected: {result['total_anomalies_detected']}")
    print(f"Severity breakdown: {result['severity_counts']}")
    
    print("\n--- Sample Anomaly ---")
    if result['anomalies']:
        # Sort by deviation to show a severe one
        sorted_anoms = sorted(result['anomalies'], key=lambda x: x['deviation_percent'], reverse=True)
        print(json.dumps(sorted_anoms[0], indent=2))
    else:
        print("No anomalies found in this dataset.")

if __name__ == "__main__":
    main()
