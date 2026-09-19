import pandas as pd
from typing import Dict, Any, List
from app.tools.anomaly_tool import AnomalyTool

class AnomalyAgent:
    def __init__(self):
        self.tool = AnomalyTool(rolling_window=24, z_threshold=3.0, contamination=0.05)

    def detect_anomalies(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str) -> Dict[str, Any]:
        """
        Receives a DataFrame and detects anomalies using multiple methods.
        Returns a structured dictionary of detected anomalies and a summary.
        """
        try:
            anomalies = self.tool.combine_anomalies(df, timestamp_col, consumption_col)
            
            # Count severity levels for summary
            high = sum(1 for a in anomalies if a["severity"] == "high")
            medium = sum(1 for a in anomalies if a["severity"] == "medium")
            low = sum(1 for a in anomalies if a["severity"] == "low")
            
            return {
                "total_anomalies_detected": len(anomalies),
                "severity_counts": {
                    "high": high,
                    "medium": medium,
                    "low": low
                },
                "anomalies": anomalies
            }
        except Exception as e:
            raise RuntimeError(f"Failed to detect anomalies: {str(e)}")
