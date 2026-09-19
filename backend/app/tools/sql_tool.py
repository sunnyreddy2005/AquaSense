import re
from typing import Dict, Any, Tuple

class SQLTool:
    def __init__(self):
        # Allowed and forbidden keywords for basic safety
        self.forbidden_keywords = [
            r'\bDROP\b', r'\bDELETE\b', r'\bUPDATE\b', r'\bINSERT\b', 
            r'\bALTER\b', r'\bTRUNCATE\b', r'\bCREATE\b', r'\bGRANT\b', 
            r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b'
        ]
        
    def validate_sql(self, query: str) -> Tuple[bool, str]:
        """
        Validates the SQL query to ensure it only performs read-only operations.
        Returns a boolean indicating if it's safe, and an error message if not.
        """
        upper_query = query.upper()
        
        # Check if it starts with a valid read operation
        if not upper_query.strip().startswith(('SELECT', 'WITH')):
            return False, "Query must start with SELECT or WITH."
            
        # Check for forbidden keywords
        for keyword in self.forbidden_keywords:
            if re.search(keyword, upper_query):
                return False, f"Forbidden keyword detected: {keyword.strip(r'\\b')}. Only read-only analytical queries are permitted."
                
        return True, "Valid"

    # NOTE: Actual execution will happen via Supabase client later in the pipeline
    def format_results(self, records: list) -> Dict[str, Any]:
        """Formats the SQL execution results into a standard dictionary."""
        return {
            "row_count": len(records),
            "data": records
        }
