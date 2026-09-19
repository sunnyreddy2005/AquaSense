import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.data_agent import DataAgent
import json
import pandas as pd

def main():
    agent = DataAgent()
    
    # Just load top 5 rows to see what it looks like before cleaning
    df_raw = pd.read_csv("../data/raw/water_consumption.csv", nrows=5)
    print("RAW HEAD:")
    print(df_raw.head())
    
    print("\nProcessing Dataset...")
    df_clean, profile, report = agent.process_dataset("../data/raw/water_consumption.csv")
    
    print("\n--- Profile ---")
    print(json.dumps(profile, indent=2))
    
    print("\n--- Cleaning Report ---")
    print(json.dumps(report, indent=2))
    
    print("\nCLEANED HEAD:")
    print(df_clean.head())
    
    df_clean.to_csv("../data/processed/cleaned_water_consumption.csv", index=False)
    print("\nSaved to data/processed/cleaned_water_consumption.csv")

if __name__ == "__main__":
    main()
