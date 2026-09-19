from typing import List, Dict, Any

class ManagerAgent:
    def __init__(self):
        # Basic heuristic keywords for routing
        self.anomaly_keywords = ['unusual', 'anomaly', 'anomalies', 'spike', 'abnormal', 'weird']
        self.pattern_keywords = ['pattern', 'trend', 'seasonal', 'recurring', 'correlate', 'relationship', 'cause']
        self.analytics_keywords = ['highest', 'lowest', 'average', 'mean', 'peak', 'total', 'compare', 'statistics']
        self.recommendation_keywords = ['conservation', 'recommendation', 'save', 'advice', 'insight']
        
    def determine_route(self, question: str) -> List[str]:
        """
        Determines the required agents and sequence based on the natural language question.
        Returns a list representing the execution path.
        """
        q_lower = question.lower()
        route = ["Manager"]
        
        needs_anomaly = any(kw in q_lower for kw in self.anomaly_keywords)
        needs_pattern = any(kw in q_lower for kw in self.pattern_keywords)
        needs_analytics = any(kw in q_lower for kw in self.analytics_keywords)
        needs_insight = any(kw in q_lower for kw in self.recommendation_keywords) or needs_anomaly or needs_pattern
        
        # Build the chain
        if needs_anomaly:
            route.append("Anomaly Agent")
        
        if needs_analytics or (not needs_anomaly and not needs_pattern and not needs_insight):
            route.append("Analytics Agent")
            
        if needs_pattern:
            route.append("Pattern Agent")
            
        if needs_insight or 'why' in q_lower:
            # If asking 'why', we need evidence from multiple places usually
            if "Anomaly Agent" not in route and "unusual" in q_lower:
                route.insert(1, "Anomaly Agent")
            if "Pattern Agent" not in route:
                route.append("Pattern Agent")
            route.append("Insight Agent")
            
        # SQL Agent fallback for specific data retrieval not covered by basic analytics
        if 'show me' in q_lower and 'all data' in q_lower:
            route.append("SQL Agent")

        return route
