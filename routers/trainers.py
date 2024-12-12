from fastapi import APIRouter, HTTPException
from database import trainers_collection,institutions_collection, sessions_collection
from models import Trainer  
import secrets
from emailservice import send_email


def generate_random_password(length=8):
    return secrets.token_urlsafe(length)[:length]

import secrets
from emailservice import send_email


def generate_random_password(length=8):
    return secrets.token_urlsafe(length)[:length]


router = APIRouter()


@router.post("/trainers/")
async def create_trainer(trainer: Trainer):
    if not trainer.institution_id:
        raise HTTPException(status_code=400, detail="Institution ID is required")
    
    # Check if the institution exists
    institution = institutions_collection.find_one({"uid": trainer.institution_id})
    if not institution:
        raise HTTPException(status_code=400, detail="Institution does not exist")
    
    # Check if the trainer already exists by email or ID
    existing_trainer = trainers_collection.find_one({"email": trainer.email})
    if existing_trainer:
        raise HTTPException(status_code=400, detail="Trainer with this email already exists")
   
    # Generate a random password for the trainer
    random_password = generate_random_password()
    trainer.password = random_password  # Store the password directly (not recommended in production)
        # Send welcome email with the generated password
    subject = "Welcome to the ClassOfOne"
    message = f"""
    Hello {trainer.name},
    
    Welcome to our platform! Your trainer account has been successfully created.
    Below are your login details:
    
    - Email: {trainer.email}
    - Password: {random_password}
    
    Institution: {institution.get('name', 'Unknown')}
    
    Please change your password upon logging in for the first time.
    Welcome to our platform! Your trainer account has been successfully created.
    Below are your login details:
    
    - Email: {trainer.email}
    - Password: {random_password}
    
    Institution: {institution.get('name', 'Unknown')}
    
    Please change your password upon logging in for the first time.

    Best regards,
    The Team
    """
    
    try:
        send_email(trainer.email, subject, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending welcome email: {str(e)}")
    

    # Insert the trainer into the trainers collection
    trainers_collection.insert_one(trainer.dict())
    
    # Add the trainer to the institution's trainers list
    institutions_collection.update_one(
        {"uid": trainer.institution_id}, 
        {"$push": {"trainers": trainer.uid}}
    )
    
    return {"message": "Trainer created successfully and added to the institution, welcome email sent"}

@router.get("/trainers/")
async def get_trainers():
    trainers = list(trainers_collection.find({}, {"_id": 0}))
    return trainers


@router.get("/trainers/{trainer_id}")
async def get_trainer(trainer_id: str):
    trainer = trainers_collection.find_one({"uid": trainer_id}, {"_id": 0})
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return trainer



@router.put("/trainers/{trainer_id}")
async def update_trainer(trainer_id: str, trainer: Trainer):
    result = trainers_collection.update_one({"uid": trainer_id}, {"$set": trainer.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return {"message": "Trainer updated successfully"}

@router.delete("/trainers/{trainer_id}")
async def delete_trainer(trainer_id: str):
    result = trainers_collection.delete_one({"uid": trainer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return {"message": "Trainer deleted successfully"}


@router.get("/trainers/institution/{institution_id}")
async def get_trainers_for_institution(institution_id: str):
    # Fetch the institution by its unique ID
    institution = institutions_collection.find_one({"uid": institution_id})
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Get the list of trainer IDs associated with the institution
    trainer_ids = institution.get("trainers", [])
    if not trainer_ids:
        raise HTTPException(status_code=404, detail="No trainers found for this institution")
    
    # Fetch trainers associated with the institution
    trainers = list(trainers_collection.find({"uid": {"$in": trainer_ids}}, {"_id": 0}))
    if not trainers:
        raise HTTPException(status_code=404, detail="No trainers found")
    
    return trainers

@router.get("/trainers/{trainer_id}/engagement")
async def get_trainer_engagement(trainer_id: str):
    sessions = list(sessions_collection.find({"trainer_ids": trainer_id}))
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this trainer")

    total_score = sum(session["average_eng_score"] or 0 for session in sessions)
    average_score = total_score / len(sessions)

    return {"trainer_id": trainer_id, "average_engagement_score": average_score}

@router.get("/engagement/overall")
async def get_overall_engagement():
    sessions = list(sessions_collection.find({}))
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found")

    total_score = sum(session["average_eng_score"] or 0 for session in sessions)
    average_score = total_score / len(sessions)

    return {"average_engagement_score": average_score}
