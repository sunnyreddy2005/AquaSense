import pandas as pd
import numpy as np
from typing import Dict, Any

class StatisticsTool:
    def __init__(self):
        pass

    def calculate_basic_stats(self, df: pd.DataFrame, consumption_col: str) -> Dict[str, float]:
        """Calculates basic aggregate statistics for the consumption column."""
        series = df[consumption_col].dropna()
        if len(series) == 0:
            return {}
            
        return {
            "total_consumption": float(series.sum()),
            "average_consumption": float(series.mean()),
            "median_consumption": float(series.median()),
            "minimum_consumption": float(series.min()),
            "maximum_consumption": float(series.max()),
            "standard_deviation": float(series.std()),
            "variance": float(series.var())
        }
        
    def aggregate_by_time(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str, freq: str) -> pd.DataFrame:
        """Aggregates consumption by a specific time frequency ('D' for daily, 'W' for weekly, 'ME' for monthly)."""
        df_temp = df.copy()
        df_temp[timestamp_col] = pd.to_datetime(df_temp[timestamp_col], errors='coerce')
        
        df_temp = df_temp.dropna(subset=[timestamp_col])
        df_temp.set_index(timestamp_col, inplace=True)
        
        # Resample and sum
        agg_df = df_temp[[consumption_col]].resample(freq).sum().reset_index()
        return agg_df

    def calculate_hourly_profile(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str) -> Dict[int, float]:
        """Calculates the average consumption for each hour of the day."""
        df_temp = df.copy()
        df_temp[timestamp_col] = pd.to_datetime(df_temp[timestamp_col], errors='coerce')
        
        df_temp['hour'] = df_temp[timestamp_col].dt.hour
        hourly_avg = df_temp.groupby('hour')[consumption_col].mean().to_dict()
        return {int(k): float(v) for k, v in hourly_avg.items()}
        
    def calculate_weekday_vs_weekend(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str) -> Dict[str, float]:
        """Compares average daily consumption on weekdays vs weekends."""
        df_temp = df.copy()
        df_temp[timestamp_col] = pd.to_datetime(df_temp[timestamp_col], errors='coerce')
            
        # First group by date to get daily totals
        df_temp['_calendar_date'] = df_temp[timestamp_col].dt.date
        df_temp['is_weekend'] = df_temp[timestamp_col].dt.dayofweek >= 5
        
        daily_totals = df_temp.groupby(['_calendar_date', 'is_weekend'])[consumption_col].sum().reset_index()
        
        weekday_avg = daily_totals[~daily_totals['is_weekend']][consumption_col].mean()
        weekend_avg = daily_totals[daily_totals['is_weekend']][consumption_col].mean()
        
        return {
            "weekday_average_daily": float(weekday_avg) if not pd.isna(weekday_avg) else 0.0,
            "weekend_average_daily": float(weekend_avg) if not pd.isna(weekend_avg) else 0.0
        }

    def find_peaks(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str) -> Dict[str, Any]:
        """Finds the absolute peak and lowest usage records."""
        if df.empty:
            return {}
            
        peak_idx = df[consumption_col].idxmax()
        low_idx = df[consumption_col].idxmin()
        
        return {
            "peak_consumption": float(df.loc[peak_idx, consumption_col]),
            "peak_timestamp": str(df.loc[peak_idx, timestamp_col]),
            "lowest_consumption": float(df.loc[low_idx, consumption_col]),
            "lowest_timestamp": str(df.loc[low_idx, timestamp_col])
        }
