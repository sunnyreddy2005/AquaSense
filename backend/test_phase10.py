import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.insight_agent import InsightAgent

def main():
    print("Initializing Insight Agent (LLM)...")
    agent = InsightAgent()
    
    question = "Why was water consumption unusually high yesterday?"
    mock_evidence = [
        {"source": "Analytics Agent", "data": {"peak_analysis": {"peak_consumption": 450.2, "peak_timestamp": "2020-07-15T18:00:00"}}},
        {"source": "Anomaly Agent", "data": {"anomalies": [{"timestamp": "2020-07-15T18:00:00", "severity": "high", "deviation_percent": 49.8}]}},
        {"source": "Pattern Agent", "data": {"contextual_relationships": [{"variable": "Temperature", "correlation_coefficient": 0.65, "strength": "strong"}]}}
    ]
    
    print("\nGenerating AI Insight based on mock evidence...")
    response = agent.generate_insight(question, mock_evidence)
    
    print("\n--- LLM Response ---")
    print(response)

if __name__ == "__main__":
    main()
