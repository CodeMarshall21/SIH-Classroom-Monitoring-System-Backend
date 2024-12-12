from fastapi import APIRouter, HTTPException
from database import users_collection,institutions_collection
from models import User

router = APIRouter()



@router.post("/users/login")
async def login(email: str, password: str):
    user = users_collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if password != user['password']:
        raise HTTPException(status_code=400, detail="Wrong Password")
    
    response = {
        "message": "Login successful",
        "email": user['email'],
        "role": user['role'],
        "uid":""
    }
    
    if user['role'] == "institution":
        # Fetch the corresponding institution
        
        institution = institutions_collection.find_one({"email": user['email']})
        print(institution)
        if institution:
            response["uid"] = institution["uid"]
    # elif user['role'] == "regulatory":
    #     # Fetch the corresponding regulatory entity
    #     # regulatory = regulatory_collection.find_one({"email": user['email']})
    #     if regulatory:
    #         response["regulatory_uid"] = regulatory["uid"]
    
    return response

@router.post("/users/")
async def create_user(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    users_collection.insert_one(user.dict())
    return {"message": "User created successfully"}

@router.get("/users/")
async def get_users():
    return list(users_collection.find({}, {"_id": 0}))

@router.get("/users/{email}")
async def get_user(email: str):
    user = users_collection.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    result = users_collection.update_one({"uid": user_id}, {"$set": user.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = users_collection.delete_one({"uid": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
