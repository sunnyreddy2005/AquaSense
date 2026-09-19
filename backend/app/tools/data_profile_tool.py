import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

class DataProfileTool:
    def __init__(self):
        self.timestamp_synonyms = ['timestamp', 'date', 'time', 'datetime']
        self.consumption_synonyms = ['consumption', 'water_usage', 'water_demand', 'usage', 'demand']

    def inspect_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Profiles the dataset to identify columns, missing values, duplicates, and calculate a quality score."""
        columns = [str(c).lower().strip() for c in df.columns]
        
        # 1. Detect Timestamp Column
        timestamp_col = None
        for col in columns:
            if any(syn in col for syn in self.timestamp_synonyms):
                timestamp_col = df.columns[columns.index(col)]
                break

        # 2. Detect Consumption Column
        consumption_col = None
        for col in columns:
            if any(syn in col for syn in self.consumption_synonyms):
                consumption_col = df.columns[columns.index(col)]
                break
                
        # 3. Context Variables
        context_cols = [c for c in df.columns if c not in [timestamp_col, consumption_col]]
        
        # 4. Metrics
        rows = len(df)
        cols = len(df.columns)
        missing_values = int(df.isnull().sum().sum())
        duplicates = int(df.duplicated().sum())
        
        # Quality Score Calculation
        # Base 100, penalize for missing values and duplicates
        missing_penalty = (missing_values / (rows * cols)) * 100 if rows > 0 and cols > 0 else 0
        dup_penalty = (duplicates / rows) * 100 if rows > 0 else 0
        
        quality_score = max(0, 100 - missing_penalty - dup_penalty)
        
        return {
            "rows": rows,
            "columns": cols,
            "timestamp_column": timestamp_col,
            "consumption_column": consumption_col,
            "context_columns": context_cols,
            "missing_values": missing_values,
            "duplicates": duplicates,
            "quality_score": round(quality_score, 1)
        }

    def clean_dataset(self, df: pd.DataFrame, profile: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Cleans the dataset based on the profile insights."""
        original_rows = len(df)
        df_clean = df.copy()
        
        timestamp_col = profile.get('timestamp_column')
        consumption_col = profile.get('consumption_column')
        
        # 1. Drop duplicates
        df_clean = df_clean.drop_duplicates()
        duplicates_removed = original_rows - len(df_clean)
        
        # 2. Handle missing timestamps
        if timestamp_col:
            missing_ts = df_clean[timestamp_col].isnull().sum()
            df_clean = df_clean.dropna(subset=[timestamp_col])
        else:
            missing_ts = 0
            
        # 3. Handle negative and missing consumption values
        missing_values_fixed = 0
        if consumption_col:
            missing_cons = df_clean[consumption_col].isnull().sum()
            if missing_cons > 0:
                df_clean[consumption_col] = df_clean[consumption_col].interpolate(method='linear').ffill().bfill()
                missing_values_fixed += int(missing_cons)
            
            # Convert non-numeric to NaN then interpolate
            df_clean[consumption_col] = pd.to_numeric(df_clean[consumption_col], errors='coerce')
            
            # Negative consumption to 0
            neg_mask = df_clean[consumption_col] < 0
            if neg_mask.any():
                df_clean.loc[neg_mask, consumption_col] = 0
                missing_values_fixed += int(neg_mask.sum())
                
        # 4. Handle other missing context
        for col in profile.get('context_columns', []):
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            missing_cnt = df_clean[col].isnull().sum()
            if missing_cnt > 0:
                df_clean[col] = df_clean[col].ffill().bfill()
                missing_values_fixed += int(missing_cnt)

        # 5. Sort by timestamp (if we can parse it)
        if timestamp_col:
            try:
                # If there are multiple date/time columns, we might need a composite, but we rely on timestamp_col
                df_clean[timestamp_col] = pd.to_datetime(df_clean[timestamp_col], errors='coerce')
                # Drop rows where timestamp coercion failed
                failed_dates = df_clean[timestamp_col].isnull().sum()
                df_clean = df_clean.dropna(subset=[timestamp_col])
                df_clean = df_clean.sort_values(by=timestamp_col).reset_index(drop=True)
            except Exception:
                pass
                
        cleaned_rows = len(df_clean)
        removed_rows = original_rows - cleaned_rows
        
        report = {
            "original_rows": original_rows,
            "cleaned_rows": cleaned_rows,
            "removed_rows": removed_rows,
            "missing_values_fixed": missing_values_fixed,
            "duplicates_removed": duplicates_removed
        }
        
        return df_clean, report
