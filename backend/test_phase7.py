import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import json
from app.agents.data_agent import DataAgent
from app.agents.anomaly_agent import AnomalyAgent
from app.agents.pattern_agent import PatternAgent

def main():
    print("Loading and cleaning data...")
    data_agent = DataAgent()
    df_clean, profile, _ = data_agent.process_dataset("data/raw/water_consumption.csv")
    
    timestamp_col = profile['timestamp_column']
    consumption_col = profile['consumption_column']
    context_cols = profile['context_columns']
    
    print("\nDetecting anomalies to pass to pattern agent...")
    anomaly_agent = AnomalyAgent()
    anomaly_result = anomaly_agent.detect_anomalies(df_clean, timestamp_col, consumption_col)
    
    print("\nInitializing Pattern Agent...")
    pattern_agent = PatternAgent()
    
    print("\nAnalyzing patterns...")
    result = pattern_agent.analyze_patterns(
        df_clean, 
        timestamp_col, 
        consumption_col, 
        context_cols, 
        anomalies=anomaly_result['anomalies']
    )
    
    print("\n--- Pattern Analysis Results ---")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
