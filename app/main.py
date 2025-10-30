from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models.entities import user, service, serviceCategory, job, vouch, review, dispute, payment, message, serviceServiceCategory

# Import route files
from app.routes import user_routes, service_routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LocaLe API",
    description="Your Community is Your Credential - Africa's trusted peer-to-peer marketplace",
    version="1.0.0"
)

# Allow frontend to connect to API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect all route files
app.include_router(user_routes.router)
app.include_router(service_routes.router)

@app.get("/")
def root():
    """Welcome message"""
    return {"message": "Welcome to LocaLe API", "status": "running"}

@app.get("/health")
def health_check():
    """Check if API is working"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000, reload=True)
    #, host="0.0.0.0"