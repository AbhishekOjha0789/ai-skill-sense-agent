from ..state import MainAgentState

def best_match_model(state: MainAgentState) -> MainAgentState:
    print("--- BEST MATCH MODEL: Running custom mathematical evaluation ---")
    
    action = state.get("action")
    target_keywords = set(k.lower() for k in state.get("keywords", []))
    profile = state.get("profile", {})
    user_interests = set(i.lower() for i in profile.get("interests", []))
    user_skills = set(profile.get("skills", []))
    
    # Gather candidate IDs from previous step
    candidate_ids = state.get("skill_ids", []) if action == "Skill" else state.get("quest_ids", [])
    
    if not candidate_ids:
        print("No candidates available for evaluation.")
        return {"best_match": None}

    # Weights for our multi-factor scoring formula
    W_KEYWORD = 0.5
    W_INTEREST = 0.3
    W_SYNERGY = 0.2

    best_candidate = None
    max_score = -1.0

    for candidate_id in candidate_ids:
        # NOTE: In a full implementation, you fetch candidate metadata (title, tags, description) 
        # from your local DataPool or DB using the candidate_id. 
        # Here is a mock representation of fetched candidate metadata:
        candidate_meta = fetch_candidate_metadata_from_datapool(candidate_id, action)
        
        cand_keywords = set(k.lower() for k in candidate_meta.get("keywords", []))
        cand_category = candidate_meta.get("category", "").lower()
        linked_skills = set(candidate_meta.get("linked_skills", []))

        # 1. Keyword Similarity (Jaccard Index)
        if target_keywords or cand_keywords:
            intersection = target_keywords.intersection(cand_keywords)
            union = target_keywords.union(cand_keywords)
            jaccard_score = len(intersection) / len(union) if union else 0.0
        else:
            jaccard_score = 0.0

        # 2. User Interest Alignment Score
        interest_match = 1.0 if any(interest in cand_category or interest in cand_keywords for interest in user_interests) else 0.0

        # 3. Synergy / Progression Bonus (Does user already have prerequisite skills?)
        synergy_score = 1.0 if linked_skills.intersection(user_skills) else 0.0

        # Calculate final weighted score
        total_score = (
            (W_KEYWORD * jaccard_score) + 
            (W_INTEREST * interest_match) + 
            (W_SYNERGY * synergy_score)
        )

        print(f"Candidate {candidate_id} Score: {total_score:.3f} (Jaccard: {jaccard_score}, Interest: {interest_match}, Synergy: {synergy_score})")

        if total_score > max_score:
            max_score = total_score
            best_candidate = candidate_id

    print(f"Successfully selected best match ID: {best_candidate} with score {max_score:.3f}")
    
    return {
        "best_match": best_candidate
    }

def fetch_candidate_metadata_from_datapool(candidate_id: str, action: str) -> dict:
    """
    Helper function to retrieve candidate metadata (keywords, category, linked skills) 
    from your DataPool storage.
    """
    # TODO: Replace with actual DB/DataPool query or API call
    return {
        "keywords": ["python", "backend", "fastapi"],
        "category": "Technology",
        "linked_skills": ["skill_242108"]
    }