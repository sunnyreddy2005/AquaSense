import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import json
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.data_agent import DataAgent

def main():
    print("Loading and cleaning data...")
    data_agent = DataAgent()
    df_clean, profile, _ = data_agent.process_dataset("data/raw/water_consumption.csv")
    
    timestamp_col = profile['timestamp_column']
    consumption_col = profile['consumption_column']
    
    print("\nInitializing Analytics Agent...")
    analytics_agent = AnalyticsAgent()
    
    print("\n--- Overview Statistics ---")
    overview = analytics_agent.generate_overview(df_clean, timestamp_col, consumption_col)
    print(json.dumps(overview, indent=2))
    
    print("\n--- Hourly Profile ---")
    hourly = analytics_agent.get_hourly_profile(df_clean, timestamp_col, consumption_col)
    print(json.dumps(hourly, indent=2))
    
    print("\n--- Testing Daily Aggregation (First 3) ---")
    daily = analytics_agent.get_time_series(df_clean, timestamp_col, consumption_col, freq='D')
    print(json.dumps(daily[:3], indent=2))

if __name__ == "__main__":
    main()
