from fastapi import FastAPI
from routers import users, institutions, sessions, slots, trainers, insights
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost:3000",  # The URL of your frontend React app
    "http://127.0.0.1:3000",  # In case the React app is running on 127.0.0.1
]

# Add CORSMiddleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
# Include routes
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(institutions.router, prefix="/api/v1", tags=["Institutions"])
app.include_router(sessions.router, prefix="/api/v1", tags=["Sessions"])
app.include_router(slots.router, prefix="/api/v1", tags=["Slots"])
app.include_router(trainers.router, prefix="/api/v1", tags=["Trainers"])
app.include_router(insights.router, prefix="/api/v1", tags=["Insights"])