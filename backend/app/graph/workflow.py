from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import (
    manager_node,
    analytics_node,
    anomaly_node,
    pattern_node,
    sql_node,
    insight_node
)

def router(state: AgentState) -> str:
    """
    Conditional router that determines the next node based on the dynamic execution route.
    """
    route = state.get("execution_route", [])
    current_index = state.get("current_step_index", 0)
    
    if current_index >= len(route):
        # We finished the dynamic tools, but we always want to end with the Insight Agent 
        # unless it was a purely analytical fetch or it's already done.
        # Actually, let's just route to END if we exhausted the list.
        return END
        
    next_agent = route[current_index]
    
    # Map string names to node names
    mapping = {
        "Analytics Agent": "analytics",
        "Anomaly Agent": "anomaly",
        "Pattern Agent": "pattern",
        "SQL Agent": "sql",
        "Insight Agent": "insight"
    }
    
    return mapping.get(next_agent, END)

def create_workflow() -> StateGraph:
    """Constructs the LangGraph state machine."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("manager", manager_node)
    workflow.add_node("analytics", analytics_node)
    workflow.add_node("anomaly", anomaly_node)
    workflow.add_node("pattern", pattern_node)
    workflow.add_node("sql", sql_node)
    workflow.add_node("insight", insight_node)
    
    # Manager is always the entry point
    workflow.set_entry_point("manager")
    
    # After manager, we route dynamically
    workflow.add_conditional_edges("manager", router)
    
    # After any execution node, we route back to the conditional router
    workflow.add_conditional_edges("analytics", router)
    workflow.add_conditional_edges("anomaly", router)
    workflow.add_conditional_edges("pattern", router)
    workflow.add_conditional_edges("sql", router)
    workflow.add_conditional_edges("insight", router)
    
    return workflow.compile()
