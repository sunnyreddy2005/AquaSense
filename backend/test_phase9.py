import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from app.graph.workflow import create_workflow
from app.graph.state import AgentState

def main():
    print("Compiling LangGraph Workflow...")
    app = create_workflow()
    
    questions = [
        "What was the highest water consumption day?",
        "Why was water consumption unusually high yesterday?"
    ]
    
    for q in questions:
        print(f"\n--- Testing Workflow for: '{q}' ---")
        
        initial_state = AgentState(
            user_question=q,
            dataset_id="test_dataset_123",
            dataset_profile=None,
            execution_route=[],
            current_step_index=0,
            analytics_results=None,
            anomaly_results=None,
            pattern_results=None,
            forecast_results=None,
            sql_results=None,
            evidence=[],
            final_response=None,
            errors=[]
        )
        
        # Invoke the graph
        result = app.invoke(initial_state)
        
        print(f"Computed Execution Route: {' -> '.join(result['execution_route'])}")
        print(f"Total Evidence Gathered: {len(result['evidence'])} items")
        print("Evidence Sources:")
        for ev in result['evidence']:
            print(f" - {ev['source']}")
            
        print(f"Final Response: {result['final_response']}")

if __name__ == "__main__":
    main()
