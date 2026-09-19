from app.graph.state import AgentState
from app.agents.manager_agent import ManagerAgent
# We import placeholders for the data logic since we don't load data globally here.
# In a real deployed app, the df would be fetched from Supabase based on dataset_id.
# For testing the graph, we'll mock the data fetching or expect it to be passed somehow.

def manager_node(state: AgentState) -> AgentState:
    """Manager analyzes the question and determines the execution route."""
    manager = ManagerAgent()
    route = manager.determine_route(state["user_question"])
    
    # Remove 'Manager' from the start if present
    if route and route[0] == "Manager":
        route = route[1:]
        
    return {
        "execution_route": route,
        "current_step_index": 0,
        "evidence": []
    }

def analytics_node(state: AgentState) -> AgentState:
    """Executes the analytics logic and appends evidence."""
    # Placeholder for actual data execution
    results = {"status": "success", "message": "Calculated analytics"}
    
    new_evidence = state.get("evidence", []).copy()
    new_evidence.append({"source": "Analytics Agent", "data": results})
    
    return {
        "analytics_results": results,
        "evidence": new_evidence,
        "current_step_index": state.get("current_step_index", 0) + 1
    }

def anomaly_node(state: AgentState) -> AgentState:
    """Executes the anomaly detection logic and appends evidence."""
    results = {"status": "success", "message": "Detected anomalies"}
    
    new_evidence = state.get("evidence", []).copy()
    new_evidence.append({"source": "Anomaly Agent", "data": results})
    
    return {
        "anomaly_results": results,
        "evidence": new_evidence,
        "current_step_index": state.get("current_step_index", 0) + 1
    }

def pattern_node(state: AgentState) -> AgentState:
    """Executes the pattern logic and appends evidence."""
    results = {"status": "success", "message": "Extracted patterns"}
    
    new_evidence = state.get("evidence", []).copy()
    new_evidence.append({"source": "Pattern Agent", "data": results})
    
    return {
        "pattern_results": results,
        "evidence": new_evidence,
        "current_step_index": state.get("current_step_index", 0) + 1
    }

def sql_node(state: AgentState) -> AgentState:
    """Executes the SQL logic and appends evidence."""
    results = {"status": "success", "message": "Ran SQL"}
    
    new_evidence = state.get("evidence", []).copy()
    new_evidence.append({"source": "SQL Agent", "data": results})
    
    return {
        "sql_results": results,
        "evidence": new_evidence,
        "current_step_index": state.get("current_step_index", 0) + 1
    }

from app.agents.insight_agent import InsightAgent

def insight_node(state: AgentState) -> AgentState:
    """The LLM node that synthesizes the accumulated evidence into a final response."""
    evidence = state.get("evidence", [])
    
    agent = InsightAgent()
    response = agent.generate_insight(state["user_question"], evidence)
    
    return {
        "final_response": response,
        "current_step_index": state.get("current_step_index", 0) + 1
    }
