import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy.stats import pearsonr

class PatternTool:
    def __init__(self):
        pass

    def analyze_temporal_patterns(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str) -> Dict[str, Any]:
        """Analyzes consumption by hour, day of week, and month to find structural patterns."""
        df_temp = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_temp[timestamp_col]):
            df_temp[timestamp_col] = pd.to_datetime(df_temp[timestamp_col], errors='coerce')
        
        df_temp = df_temp.dropna(subset=[timestamp_col])
        
        df_temp['hour'] = df_temp[timestamp_col].dt.hour
        df_temp['day_of_week'] = df_temp[timestamp_col].dt.day_name()
        df_temp['month'] = df_temp[timestamp_col].dt.month_name()
        
        hourly_avg = df_temp.groupby('hour')[consumption_col].mean()
        day_avg = df_temp.groupby('day_of_week')[consumption_col].mean()
        month_avg = df_temp.groupby('month')[consumption_col].mean()
        
        peak_hour = int(hourly_avg.idxmax()) if not hourly_avg.empty else None
        low_hour = int(hourly_avg.idxmin()) if not hourly_avg.empty else None
        peak_day = str(day_avg.idxmax()) if not day_avg.empty else None
        peak_month = str(month_avg.idxmax()) if not month_avg.empty else None
        
        return {
            "peak_usage_periods": {
                "hour": peak_hour,
                "day_of_week": peak_day,
                "month": peak_month
            },
            "low_usage_periods": {
                "hour": low_hour
            }
        }

    def analyze_contextual_relationships(self, df: pd.DataFrame, consumption_col: str, context_cols: List[str]) -> List[Dict[str, Any]]:
        """Finds statistical correlations between water usage and context variables (like temp, rain)."""
        relationships = []
        df_clean = df.dropna(subset=[consumption_col] + context_cols)
        
        for col in context_cols:
            if col not in df_clean.columns:
                continue
            
            # Make sure it is numeric
            if not pd.api.types.is_numeric_dtype(df_clean[col]):
                continue
                
            x = df_clean[col].values
            y = df_clean[consumption_col].values
            
            if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
                continue
                
            corr, p_value = pearsonr(x, y)
            
            # Only report significant correlations
            if p_value < 0.05 and abs(corr) > 0.1:
                direction = "increased" if corr > 0 else "decreased"
                strength = "strong" if abs(corr) > 0.5 else "moderate" if abs(corr) > 0.3 else "weak"
                
                # Careful causal language
                insight = f"Consumption generally {direction} during periods where {col} was higher. Note: This indicates a {strength} correlation, but not necessarily a direct causal relationship."
                
                relationships.append({
                    "variable": col,
                    "correlation_coefficient": round(float(corr), 2),
                    "p_value": round(float(p_value), 4),
                    "strength": strength,
                    "insight": insight
                })
                
        return relationships

    def detect_recurring_anomalies(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyzes historical anomalies to identify recurring temporal patterns."""
        if not anomalies:
            return {"recurring_patterns": False, "details": "No anomalies provided."}
            
        df_anom = pd.DataFrame(anomalies)
        df_anom['timestamp'] = pd.to_datetime(df_anom['timestamp'], errors='coerce')
        df_anom = df_anom.dropna(subset=['timestamp'])
        
        if df_anom.empty:
            return {"recurring_patterns": False, "details": "Invalid timestamps."}
            
        df_anom['hour'] = df_anom['timestamp'].dt.hour
        
        # Check if anomalies cluster in a specific hour
        hour_counts = df_anom['hour'].value_counts()
        recurring = False
        details = []
        
        if not hour_counts.empty and hour_counts.iloc[0] > max(2, len(df_anom) * 0.3):
            recurring = True
            details.append(f"Anomalies frequently recur around hour {hour_counts.index[0]}.00.")
            
        return {
            "recurring_patterns": recurring,
            "details": " ".join(details) if details else "No clear recurring temporal pattern found among the anomalies."
        }
