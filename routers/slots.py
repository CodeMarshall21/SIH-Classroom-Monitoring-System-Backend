from fastapi import APIRouter, HTTPException
from database import slots_collection,sessions_collection,institutions_collection
from models import Slot, SlotUpdate

router = APIRouter()

@router.post("/slots/")
async def create_slot(slot: Slot):
    slots_collection.insert_one(slot.dict())
    
    session = sessions_collection.find_one({"uid": slot.session_id})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions_collection.update_one(
        {"uid": slot.session_id},
        {"$push": {"slots": slot.uid}}
    )
    
    return {"message": "Slot created successfully and session updated"}


@router.get("/slots/")
async def get_slots():
    return list(slots_collection.find({}, {"_id": 0}))

@router.get("/slots/{slot_id}")
async def get_slot(slot_id: str):
    slot = slots_collection.find_one({"uid": slot_id}, {"_id": 0})
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot

# @router.put("/slots/{slot_id}")
# async def update_slot(slot_id: str, slot: Slot):
#     result = slots_collection.update_one({"id": slot_id}, {"$set": slot.dict()})
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Slot not found")
#     return {"message": "Slot updated successfully"}

async def update_institution_average_engagement(institution_id: str):
    # Fetch all sessions associated with the institution
    sessions = list(sessions_collection.find({"institution_id": institution_id}))
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this institution")

    # Calculate the average score for the institution
    total_score = sum(session["average_eng_score"] or 0 for session in sessions)
    average_score = total_score / len(sessions)

    # Determine the institution's status based on the average score
    if 0 <= average_score < 50:
        status = "poor"
    elif 50 <= average_score < 75:
        status = "average"
    else:
        status = "excellent"

    # Update the institution's average score and status
    institutions_collection.update_one(
        {"uid": institution_id},
        {"$set": {"average_score": average_score, "status": status}}
    )



async def update_session_average_engagement(session_id: str, SlotUpdate: SlotUpdate):
    slots = list(slots_collection.find({"session_id": session_id}))
    if not slots:
        raise HTTPException(status_code=404, detail="No slots found for this session")

    total_score = sum(slot["engagement_score"] or 0 for slot in slots)
    average_score = total_score / len(slots)

    sessions_collection.update_one({"uid": session_id}, {"$set": {"average_eng_score": average_score}})

    session = sessions_collection.find_one({"uid": session_id})
    institution_id = session["institution_id"]

    await update_institution_average_engagement(institution_id)
    print("Successfully updated")


@router.put("/slots/{slot_id}")
async def update_slot(slot_id: str, slot: Slot):
    result = slots_collection.update_one({"uid": slot_id}, {"$set": slot.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    updated_slot = slots_collection.find_one({"uid": slot_id})
    session_id = updated_slot["session_id"]
    print("Successfully updated")

    await update_session_average_engagement(session_id)
    print("Successfully updated 2")

    return {"message": "Slot updated successfully and related scores recalculated"}



#used by AI model to update engagement_scores
@router.patch("/slots/{slot_id}")
async def update_slot(slot_id: str, slot: Slot):
    update_fields = slot.dict(exclude_unset=True)

    result = slots_collection.update_one({"uid": slot_id}, {"$set": update_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    updated_slot = slots_collection.find_one({"uid": slot_id})
    session_id = updated_slot["session_id"]

    await update_session_average_engagement(session_id)

    return {"message": "Slot updated successfully and related scores recalculated"}



@router.delete("/slots/{slot_id}")
async def delete_slot(slot_id: str):
    result = slots_collection.delete_one({"uid": slot_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Slot not found")
    return {"message": "Slot deleted successfully"}


