from fastapi import APIRouter, HTTPException
from database import slots_collection, sessions_collection, institutions_collection, trainers_collection, users_collection


router = APIRouter()


@router.get("/insights")
async def get_all_insights():
    # Calculate overall average engagement score
    sessions = list(sessions_collection.find({}))
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found")
    
    # Filter out None values and calculate total score
    valid_scores = [session["average_eng_score"] for session in sessions if session["average_eng_score"] is not None]
    total_score = sum(valid_scores)
    overall_average_engagement_score = total_score / len(valid_scores) if valid_scores else 0

    # Get number of sessions
    num_sessions = len(sessions)

    # Get number of institutions
    num_institutions = institutions_collection.count_documents({})

    # Get number of trainers
    num_trainers = trainers_collection.count_documents({})

    # Get number of slots
    num_slots = slots_collection.count_documents({})

    return {
        "overall_average_engagement_score": overall_average_engagement_score,
        "num_sessions": num_sessions,
        "num_institutions": num_institutions,
        "num_trainers": num_trainers,
        "num_slots": num_slots
    }
