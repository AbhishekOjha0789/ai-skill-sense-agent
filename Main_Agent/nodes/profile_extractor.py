import requests
from state import MainAgentState

def profile_extractor(state: MainAgentState) -> MainAgentState:
    print("--- PROFILE EXTRACTOR: Fetching comprehensive user profile ---")
    user_id = state.get("user_id")
    
    if not user_id:
        print("Error: No user_id found in state.")
        return {"profile": {}}

    try:
        # Request user profile from your FastAPI backend using the defined schema
        response = requests.get(
            f"https://your-backend-api.com/api/users/{user_id}/profile"
        )
        
        if response.status_code == 200:
            profile_data = response.json()
            
            # Mapping profile data based on your schema structure:
            # - Required fields: user_id, username, email, age, gender, interests, skills, active_quests, completed_quest, failed_quests, summary[cite: 8]
            # - Optional fields: occupation, experience, education_status, education_summary[cite: 8]
            
            return {
                "profile": {
                    "user_id": profile_data.get("user_id"),
                    "username": profile_data.get("username"),
                    "email": profile_data.get("email"),
                    "age": profile_data.get("age"),
                    "gender": profile_data.get("gender"),
                    "interests": profile_data.get("interests", []),
                    "skills": profile_data.get("skills", []),
                    "active_quests": profile_data.get("active_quests", []),
                    "completed_quest": profile_data.get("completed_quest", []),
                    "failed_quests": profile_data.get("failed_quests", []),
                    "summary": profile_data.get("summary", ""),
                    "occupation": profile_data.get("occupation"),
                    "experience": profile_data.get("experience"),
                    "education_status": profile_data.get("education_status"),
                    "education_summary": profile_data.get("education_summary")
                }
            }
        else:
            print(f"Failed to fetch profile. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error communicating with backend API for profile extraction: {e}")
        
    return {"profile": {}}