from fastapi import APIRouter, HTTPException
from database import institutions_collection,sessions_collection,users_collection
from models import Institution
import secrets
from emailservice import send_email

router = APIRouter()

def generate_random_password(length=8):
    return secrets.token_urlsafe(length)[:length]

@router.post("/institutions/")
async def create_institution(institution: Institution):

    existing_institution = institutions_collection.find_one({"$or": [{"email": institution.email}, {"name": institution.name}]})
    if existing_institution:
        raise HTTPException(
            status_code=400, 
            detail="An institution with this email or name already exists"
        )
    
    random_password = generate_random_password()
    institution.password = random_password  
    
    institutions_collection.insert_one(institution.dict())
    
    user_entry = {
        "email": institution.email,
        "password": institution.password,  # Consider hashing the password before storing
        "role": "institution",
        "name": institution.name,
        "id": institution.uid  # Ensure `uid` is part of the `Institution` model
    }
    
    users_collection.insert_one(user_entry)
    
    subject = "Welcome to the ClassOfOne"
    message = f"""
    Hello {institution.name},
    
    Welcome to our platform! Your institution account has been successfully created.
    Below are your login details:
    
    - Email: {institution.email}
    - Password: {random_password}
    
    Please change your password upon logging in for the first time.

    Best regards,
    The Team Poriyaalargal
    """
    
    # Send the email
    try:
        send_email(institution.email, subject, message)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error sending welcome email: {str(e)}"
        )
    
    
    
    return {"message": "Institution created successfully and welcome email sent"}

@router.get("/institutions/")
async def get_institutions():
    return list(institutions_collection.find({}, {"_id": 0}))



@router.get("/institutions/{institution_id}")
async def get_institution(institution_id: str):
    institution = institutions_collection.find_one({"uid": institution_id}, {"_id": 0})
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    return institution


@router.put("/institutions/{institution_id}")
async def update_institution(institution_id: str, institution: Institution):
    result = institutions_collection.update_one({"uid": institution_id}, {"$set": institution.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Institution not found")
    return {"message": "Institution updated successfully"}


@router.delete("/institutions/{institution_id}")
async def delete_institution(institution_id: str):
    result = institutions_collection.delete_one({"uid": institution_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Institution not found")
    return {"message": "Institution deleted successfully"}



# @router.get("/institutions/{institution_id}/trainers")
# async def get_trainers_for_institution(institution_id: str):
#     institution = institutions_collection.find_one({"uid": institution_id})
#     print(institution)
#     if not institution:
#         raise HTTPException(status_code=404, detail="Institution not found")
    
#     trainer_ids = institution.get("trainers", [])

    
#     if not trainer_ids:
#         raise HTTPException(status_code=404, detail="No trainers found for this institution")
    
#     # Fetch trainers associated with the institution
#     trainers = list(trainers_collection.find({"uid": {"$in": trainer_ids}}, {"_id": 0}))
    
#     if not trainers:
#         raise HTTPException(status_code=404, detail="No trainers found")
    
#     return trainers


# @router.get("/institutions/{institution_id}/sessions")
# async def get_sessions_for_institution(institution_id: str):
#     # Fetch the institution to check if it exists
#     institution = institutions_collection.find_one({"uid": institution_id})
#     if not institution:
#         raise HTTPException(status_code=404, detail="Institution not found")
    
#     # Fetch sessions associated with the institution
#     sessions = list(sessions_collection.find({"institution_id": institution_id}, {"_id": 0}))
    
#     if not sessions:
#         raise HTTPException(status_code=404, detail="No sessions found for this institution")
    
#     return sessions




# # Edit session
# @router.patch("/institutions/{institution_id}/sessions/{session_id}")
# async def update_session_for_institution(institution_id: str, session_id: str, session: Session):
#     institution = institutions_collection.find_one({"id": institution_id})
#     if not institution:
#         raise HTTPException(status_code=404, detail="Institution not found")
    
#     existing_session = sessions_collection.find_one({"id": session_id, "institution_id": institution_id})
#     if not existing_session:
#         raise HTTPException(status_code=404, detail="Session not found for this institution")
    
#     session_data = session.dict(exclude_unset=True)  
#     result = sessions_collection.update_one({"id": session_id, "institution_id": institution_id}, {"$set": session_data})
    
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Session update failed")
    
#     return {"message": "Session updated successfully"}

@router.get("/institutions/{institution_id}/engagement")
async def get_institution_engagement(institution_id: str):
    sessions = list(sessions_collection.find({"institution_id": institution_id}))
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this institution")

    total_score = sum(session["average_eng_score"] or 0 for session in sessions)
    average_score = total_score / len(sessions)

    return {"institution_id": institution_id, "average_engagement_score": average_score}
