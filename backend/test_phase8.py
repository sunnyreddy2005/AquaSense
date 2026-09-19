import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.manager_agent import ManagerAgent
from app.agents.sql_agent import SQLAgent

def main():
    print("--- Testing Manager Agent Routing ---")
    manager = ManagerAgent()
    
    questions = [
        "What was the highest water consumption day?",
        "Show unusual water consumption.",
        "Why was water consumption unusually high yesterday?",
        "Give me conservation recommendations."
    ]
    
    for q in questions:
        route = manager.determine_route(q)
        print(f"Question: {q}")
        print(f"Route: {' -> '.join(route)}\n")
        
    print("--- Testing SQL Agent Validation ---")
    sql_agent = SQLAgent()
    
    queries = [
        "SELECT * FROM water_consumption WHERE consumption > 500;",
        "DELETE FROM datasets WHERE id = 1;",
        "WITH daily AS (SELECT date, SUM(consumption) as total FROM water_consumption GROUP BY date) SELECT * FROM daily ORDER BY total DESC;"
    ]
    
    for q in queries:
        is_valid, clean_sql, msg = sql_agent.parse_and_validate(q)
        print(f"Query: {q}")
        print(f"Valid: {is_valid} | Message: {msg}\n")

if __name__ == "__main__":
    main()
