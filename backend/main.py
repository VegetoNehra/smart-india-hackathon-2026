from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base, SessionLocal
from app.models import domain # Import models so SQLAlchemy knows about them
from app.services.data_service import seed_initial_data
from app.api.router import router as api_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Seed the database with initial mock data
db = SessionLocal()
try:
    seed_initial_data(db)
finally:
    db.close()

app = FastAPI(
    title="Monsoon Intelligence API",
    description="Backend for the SMART INDIA HACKATHON Monsoon Prediction System",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routes under /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Monsoon Intelligence API is running"}

