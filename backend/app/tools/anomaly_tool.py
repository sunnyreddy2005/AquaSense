import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any

class AnomalyTool:
    def __init__(self, rolling_window: int = 24, z_threshold: float = 3.0, contamination: float = 0.05):
        self.rolling_window = rolling_window
        self.z_threshold = z_threshold
        self.contamination = contamination

    def detect_rolling_baseline(self, df: pd.DataFrame, consumption_col: str) -> pd.Series:
        """Detect anomalies based on a rolling mean and standard deviation."""
        rolling_mean = df[consumption_col].rolling(window=self.rolling_window, min_periods=1).mean()
        rolling_std = df[consumption_col].rolling(window=self.rolling_window, min_periods=1).std().fillna(0)
        
        # Consider anomalous if it's > rolling_mean + 3*rolling_std
        upper_bound = rolling_mean + (self.z_threshold * rolling_std)
        return df[consumption_col] > upper_bound

    def detect_z_score(self, df: pd.DataFrame, consumption_col: str) -> pd.Series:
        """Detect anomalies using global Z-Score."""
        mean = df[consumption_col].mean()
        std = df[consumption_col].std()
        
        if std == 0:
            return pd.Series([False] * len(df))
            
        z_scores = (df[consumption_col] - mean) / std
        return z_scores > self.z_threshold

    def detect_isolation_forest(self, df: pd.DataFrame, consumption_col: str) -> pd.Series:
        """Detect anomalies using Isolation Forest."""
        X = df[[consumption_col]].fillna(0).values
        clf = IsolationForest(contamination=self.contamination, random_state=42)
        preds = clf.fit_predict(X)
        # Isolation forest returns -1 for outliers and 1 for inliers
        # We also want to make sure it's an unusually *high* value (anomalous spike), 
        # though it detects both. We'll mark as anomaly if -1 AND value > median.
        median_val = df[consumption_col].median()
        return (preds == -1) & (df[consumption_col] > median_val)

    def combine_anomalies(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str) -> List[Dict[str, Any]]:
        """Run all 3 methods and combine results into a structured format."""
        df_eval = df.copy()
        
        if not pd.api.types.is_datetime64_any_dtype(df_eval[timestamp_col]):
            df_eval[timestamp_col] = pd.to_datetime(df_eval[timestamp_col], errors='coerce')
        
        # Sort chronologically for rolling window to work correctly
        df_eval = df_eval.sort_values(timestamp_col).reset_index(drop=True)

        rolling_flags = self.detect_rolling_baseline(df_eval, consumption_col)
        z_flags = self.detect_z_score(df_eval, consumption_col)
        if_flags = self.detect_isolation_forest(df_eval, consumption_col)
        
        # Compute baselines for reporting
        rolling_mean = df_eval[consumption_col].rolling(window=self.rolling_window, min_periods=1).mean()
        
        anomalies = []
        for i in range(len(df_eval)):
            methods = []
            if rolling_flags.iloc[i]: methods.append("rolling_baseline")
            if z_flags.iloc[i]: methods.append("z_score")
            if if_flags.iloc[i]: methods.append("isolation_forest")
            
            if methods:
                observed = float(df_eval.loc[i, consumption_col])
                baseline = float(rolling_mean.iloc[i])
                
                # Protect against division by zero
                deviation_percent = 0.0
                if baseline > 0:
                    deviation_percent = ((observed - baseline) / baseline) * 100
                elif observed > 0:
                    deviation_percent = 100.0
                    
                # Severity heuristic based on number of methods and deviation
                severity = "low"
                if len(methods) >= 3 or deviation_percent > 50:
                    severity = "high"
                elif len(methods) == 2 or deviation_percent > 30:
                    severity = "medium"

                anomalies.append({
                    "timestamp": str(df_eval.loc[i, timestamp_col]),
                    "observed_value": round(observed, 2),
                    "baseline": round(baseline, 2),
                    "deviation_percent": round(deviation_percent, 1),
                    "severity": severity,
                    "methods_detected": methods
                })
                
        return anomalies
