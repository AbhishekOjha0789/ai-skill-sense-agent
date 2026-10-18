from ..state import MainAgentState


def best_match_model(state: MainAgentState) -> MainAgentState:
    print("--- BEST MATCH MODEL: Running custom mathematical evaluation ---")

    action = state.get("action")
    target_keywords = {str(k).lower() for k in (state.get("keywords") or [])}
    profile = state.get("profile") or {}
    user_interests = {str(i).lower() for i in (profile.get("interests") or [])}

    # Skills may be strings or dicts; normalise to a set of ids/names
    user_skills = set()
    for s in profile.get("skills") or []:
        if isinstance(s, dict):
            val = s.get("skill_id") or s.get("id") or s.get("name")
            if val:
                user_skills.add(str(val))
        else:
            user_skills.add(str(s))

    candidate_ids = (
        state.get("skill_ids") if action == "Skill" else state.get("quest_ids")
    ) or []

    if not candidate_ids:
        print("No candidates available for evaluation.")
        return {"best_match": None}

    W_KEYWORD, W_INTEREST, W_SYNERGY = 0.5, 0.3, 0.2

    best_candidate = None
    max_score = -1.0

    for candidate_id in candidate_ids:
        meta = fetch_candidate_metadata_from_datapool(candidate_id, action) or {}

        cand_keywords = {str(k).lower() for k in (meta.get("keywords") or [])}
        cand_category = (meta.get("category") or "").lower()
        linked_skills = {str(s) for s in (meta.get("linked_skills") or [])}

        # 1. Keyword similarity (Jaccard)
        union = target_keywords | cand_keywords
        jaccard_score = len(target_keywords & cand_keywords) / len(union) if union else 0.0

        # 2. Interest alignment
        interest_match = (
            1.0
            if any(i in cand_category or i in cand_keywords for i in user_interests)
            else 0.0
        )

        # 3. Synergy / progression bonus
        synergy_score = 1.0 if linked_skills & user_skills else 0.0

        total_score = (
            W_KEYWORD * jaccard_score
            + W_INTEREST * interest_match
            + W_SYNERGY * synergy_score
        )

        print(
            f"Candidate {candidate_id} Score: {total_score:.3f} "
            f"(Jaccard: {jaccard_score:.3f}, Interest: {interest_match}, Synergy: {synergy_score})"
        )

        if total_score > max_score:
            max_score = total_score
            best_candidate = candidate_id

    print(f"Successfully selected best match ID: {best_candidate} with score {max_score:.3f}")
    return {"best_match": best_candidate}


def fetch_candidate_metadata_from_datapool(candidate_id: str, action: str) -> dict:
    """
    Retrieve candidate metadata (keywords, category, linked skills) from your DataPool.
    """
    # TODO: Replace with actual DB/DataPool query or API call
    return {
        "keywords": ["python", "backend", "fastapi"],
        "category": "Technology",
        "linked_skills": ["skill_242108"],
    }