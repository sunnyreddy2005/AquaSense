from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    """
    Represents the shared state of the LangGraph workflow.
    """
    user_question: str
    dataset_id: Optional[str]
    dataset_profile: Optional[Dict[str, Any]]
    
    # Manager outputs
    execution_route: List[str]
    current_step_index: int
    
    # Tool/Agent results
    analytics_results: Optional[Dict[str, Any]]
    anomaly_results: Optional[Dict[str, Any]]
    pattern_results: Optional[Dict[str, Any]]
    forecast_results: Optional[Dict[str, Any]]
    sql_results: Optional[Dict[str, Any]]
    
    # Accumulated context
    evidence: List[Dict[str, Any]]
    
    # Final outputs
    final_response: Optional[str]
    errors: List[str]
