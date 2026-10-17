from ..state import MainAgentState

def check_database_updates(state: MainAgentState) -> MainAgentState:
    print(f"--- AGENT TRIGGERED: Processing Update ID: {state.get('update_id')} for User ID: {state.get('user_id')} ---")
    
    # The payload is already injected via the FastAPI trigger endpoint.
    # You can validate or log it here before handing off to the queue or profile extractor.
    
    return state