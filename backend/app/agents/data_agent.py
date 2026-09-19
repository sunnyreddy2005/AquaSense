from typing import Dict, Any, Tuple
import pandas as pd
from app.tools.data_profile_tool import DataProfileTool

class DataAgent:
    def __init__(self):
        self.tool = DataProfileTool()

    def process_dataset(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
        """
        Loads a CSV, profiles it, and cleans it.
        Returns the cleaned DataFrame, the profile report, and the cleaning report.
        """
        try:
            # Load the dataset
            df = pd.read_csv(file_path)
            
            # Profile the raw dataset
            profile = self.tool.inspect_dataset(df)
            
            # Clean the dataset
            df_clean, cleaning_report = self.tool.clean_dataset(df, profile)
            
            # Reprofile after cleaning to update metrics
            post_clean_profile = self.tool.inspect_dataset(df_clean)
            
            return df_clean, post_clean_profile, cleaning_report
            
        except Exception as e:
            raise RuntimeError(f"Error processing dataset: {str(e)}")
