from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "fastapi_project"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Collections
users_collection = db["users"]
institutions_collection = db["institutions"]
sessions_collection = db["sessions"]
slots_collection = db["slots"]
trainers_collection = db["trainers"]
regulatory_collection = db["regulatory"]