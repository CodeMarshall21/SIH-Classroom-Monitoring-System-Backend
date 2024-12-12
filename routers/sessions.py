from fastapi import APIRouter, HTTPException
from database import sessions_collection, trainers_collection,slots_collection,institutions_collection
from models import Session,Slot
from emailservice import send_email



router = APIRouter()

@router.post("/sessions/")
async def create_session(session: Session):
    institution = institutions_collection.find_one({"uid": session.institution_id})
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
   
    for slot in session.slots:
        slot.session_id = session.uid  

    slots_data = [slot.dict() for slot in session.slots]  
    slots_collection.insert_many(slots_data)  

    session_data = session.dict()  
    sessions_collection.insert_one(session_data) 
    institutions_collection.update_one(
        {"uid": session.institution_id},
        {"$push": {"sessions": session.uid}} 
    )


    return {
        "message": "Session created successfully with slots linked and stored.",
        "session_id": session.uid
    }

@router.get("/sessions/")
async def get_sessions():
    return list(sessions_collection.find({}, {"_id": 0}))

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = sessions_collection.find_one({"uid": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/sessions/{session_id}")
async def update_session(session_id: str, session: Session):
    result = sessions_collection.update_one({"uid": session_id}, {"$set": session.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session updated successfully"}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    result = sessions_collection.delete_one({"uid": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}

@router.get("/sessions/{session_id}/slots")
async def get_slots_for_session(session_id: str):
    # First, check if the session exists
    session = sessions_collection.find_one({"uid": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Now, fetch slots from the slots collection that belong to this session
    slots = slots_collection.find({"session_id": session_id}, {"_id": 0})
    
    # If no slots are found, raise an error
    slots_list = list(slots)
    if not slots_list:
        raise HTTPException(status_code=404, detail="No slots found for this session")
    return slots_list

@router.patch("/sessions/{session_id}/slots")
async def update_slots_for_session(session_id: str, slot: Slot):
    # First, check if the session exists
    session = sessions_collection.find_one({"uid": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    slot_data = slot.dict(exclude_unset=True)
    
   
    if "uid" in slot_data:
        result = slots_collection.update_one({"uid": slot_data["uid"], "session_id": session_id}, {"$set": slot_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Slot not found for the given session")
        return {"message": "Slot updated successfully"}
    else:
        slot_data["session_id"] = session_id  
        slots_collection.insert_one(slot_data)
        return {"message": "Slot created successfully"}

@router.get("/sessions/institution/{institution_id}")
async def get_sessions_for_institution(institution_id: str):
    # Check if the institution exists
    institution = institutions_collection.find_one({"uid": institution_id})
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Retrieve all sessions associated with the institution
    sessions = list(sessions_collection.find({"institution_id": institution_id}, {"_id": 0}))
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this institution")
    
    return sessions

@router.get("/sessions/{session_id}/engagement")
async def get_session_engagement(session_id: str):
    slots = list(slots_collection.find({"session_id": session_id}))
    if not slots:
        raise HTTPException(status_code=404, detail="No slots found for this session")
    

    total_score = sum(slot["engagement_score"] or 0 for slot in slots)
    average_score = total_score / len(slots)

    return {"session_id": session_id, "average_engagement_score": average_score}
