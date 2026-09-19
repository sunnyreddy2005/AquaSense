import pandas as pd
from typing import Dict, Any, List
from app.tools.statistics_tool import StatisticsTool

class AnalyticsAgent:
    def __init__(self):
        self.tool = StatisticsTool()

    def generate_overview(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str) -> Dict[str, Any]:
        """Generates a comprehensive statistical overview of the dataset."""
        basic_stats = self.tool.calculate_basic_stats(df, consumption_col)
        peaks = self.tool.find_peaks(df, timestamp_col, consumption_col)
        weekday_vs_weekend = self.tool.calculate_weekday_vs_weekend(df, timestamp_col, consumption_col)
        
        # Combine all overview metrics
        return {
            "basic_statistics": basic_stats,
            "peak_analysis": peaks,
            "weekday_vs_weekend": weekday_vs_weekend
        }
        
    def get_time_series(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str, freq: str = 'D') -> List[Dict[str, Any]]:
        """Returns time series aggregated data (e.g. Daily or Monthly)."""
        agg_df = self.tool.aggregate_by_time(df, timestamp_col, consumption_col, freq)
        # Convert timestamp to string for JSON serialization
        agg_df[timestamp_col] = agg_df[timestamp_col].dt.strftime('%Y-%m-%d')
        return agg_df.to_dict(orient='records')
        
    def get_hourly_profile(self, df: pd.DataFrame, timestamp_col: str, consumption_col: str) -> Dict[int, float]:
        """Returns the average consumption per hour of the day."""
        return self.tool.calculate_hourly_profile(df, timestamp_col, consumption_col)
