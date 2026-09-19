import pandas as pd
from typing import Dict, Any, List
from app.tools.pattern_tool import PatternTool

class PatternAgent:
    def __init__(self):
        self.tool = PatternTool()

    def analyze_patterns(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str, context_cols: List[str], anomalies: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Conducts a full pattern analysis on the dataset.
        Combines temporal structural patterns, contextual correlations, and recurring anomaly checks.
        """
        try:
            temporal = self.tool.analyze_temporal_patterns(df, timestamp_col, consumption_col)
            relationships = self.tool.analyze_contextual_relationships(df, consumption_col, context_cols)
            
            recurring_anomalies = {"recurring_patterns": False, "details": "No anomalies provided."}
            if anomalies:
                recurring_anomalies = self.tool.detect_recurring_anomalies(anomalies)
                
            return {
                "temporal_patterns": temporal,
                "contextual_relationships": relationships,
                "recurring_anomalies": recurring_anomalies
            }
        except Exception as e:
            raise RuntimeError(f"Failed to analyze patterns: {str(e)}")
