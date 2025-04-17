from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
mock_assets = [
    {
        "id": "asset-001",
        "name": "Character - Hero",
        "asset_type": "character",
        "status": "in_progress",
        "version": 3,
        "description": "Main character model",
        "metadata": {
            "artist": "John Doe",
            "department": "Character",
            "polygons": 12500
        },
        "created_at": "2023-09-15T10:30:00Z",
        "updated_at": "2023-10-05T14:45:00Z"
    },
    {
        "id": "asset-002",
        "name": "Environment - Forest",
        "asset_type": "environment",
        "status": "approved",
        "version": 5,
        "description": "Main forest environment",
        "metadata": {
            "artist": "Jane Smith",
            "department": "Environment",
            "area": "Main Forest"
        },
        "created_at": "2023-08-20T09:15:00Z",
        "updated_at": "2023-10-10T11:20:00Z"
    },
    {
        "id": "asset-003",
        "name": "Prop - Magic Sword",
        "asset_type": "prop",
        "status": "completed",
        "version": 2,
        "description": "Hero's magical sword",
        "metadata": {
            "artist": "Mike Johnson",
            "department": "Props",
            "material": "Metal"
        },
        "created_at": "2023-09-25T13:45:00Z",
        "updated_at": "2023-10-12T16:30:00Z"
    },
    {
        "id": "asset-004",
        "name": "Vehicle - Spaceship",
        "asset_type": "vehicle",
        "status": "in_review",
        "version": 4,
        "description": "Main spaceship model",
        "metadata": {
            "artist": "Sarah Williams",
            "department": "Vehicles",
            "size": "Large"
        },
        "created_at": "2023-09-10T08:20:00Z",
        "updated_at": "2023-10-08T09:15:00Z"
    },
    {
        "id": "asset-005",
        "name": "Character - Villain",
        "asset_type": "character",
        "status": "in_progress",
        "version": 2,
        "description": "Main villain model",
        "metadata": {
            "artist": "Robert Chen",
            "department": "Character",
            "polygons": 15000
        },
        "created_at": "2023-09-18T11:30:00Z",
        "updated_at": "2023-10-07T13:45:00Z"
    }
]

mock_shots = [
    {
        "id": "shot-001",
        "name": "Opening Scene",
        "sequence": "seq001",
        "frameStart": 1001,
        "frameEnd": 1124,
        "status": "in_progress",
        "version": 2,
        "description": "Opening scene with hero",
        "assets": ["asset-001", "asset-002"],
        "created_at": "2023-09-20T09:30:00Z",
        "updated_at": "2023-10-08T15:45:00Z"
    },
    {
        "id": "shot-002",
        "name": "Hero vs Villain",
        "sequence": "seq003",
        "frameStart": 3045,
        "frameEnd": 3156,
        "status": "in_review",
        "version": 3,
        "description": "Battle scene between hero and villain",
        "assets": ["asset-001", "asset-003", "asset-005"],
        "created_at": "2023-09-22T10:15:00Z",
        "updated_at": "2023-10-10T14:30:00Z"
    },
    {
        "id": "shot-003",
        "name": "Spaceship Landing",
        "sequence": "seq002",
        "frameStart": 2078,
        "frameEnd": 2145,
        "status": "completed",
        "version": 4,
        "description": "Spaceship landing in forest",
        "assets": ["asset-004", "asset-002"],
        "created_at": "2023-09-18T11:45:00Z",
        "updated_at": "2023-10-12T16:20:00Z"
    },
    {
        "id": "shot-004",
        "name": "Forest Chase",
        "sequence": "seq004",
        "frameStart": 4012,
        "frameEnd": 4189,
        "status": "in_progress",
        "version": 1,
        "description": "Chase scene through forest",
        "assets": ["asset-001", "asset-002", "asset-003"],
        "created_at": "2023-09-25T13:30:00Z",
        "updated_at": "2023-10-09T10:45:00Z"
    },
    {
        "id": "shot-005",
        "name": "Final Battle",
        "sequence": "seq005",
        "frameStart": 5001,
        "frameEnd": 5234,
        "status": "not_started",
        "version": 1,
        "description": "Final battle scene",
        "assets": ["asset-001", "asset-003", "asset-005"],
        "created_at": "2023-09-28T14:15:00Z",
        "updated_at": "2023-09-28T14:15:00Z"
    }
]

# Asset endpoints
@app.get("/api/v1/assets/")
async def get_assets():
    return mock_assets

@app.get("/api/v1/assets/{asset_id}")
async def get_asset(asset_id: str):
    for asset in mock_assets:
        if asset["id"] == asset_id:
            return asset
    raise HTTPException(status_code=404, detail="Asset not found")

@app.post("/api/v1/assets/")
async def create_asset(asset: Dict[str, Any]):
    new_asset = {
        "id": f"asset-{str(uuid.uuid4())[:8]}",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        **asset
    }
    mock_assets.append(new_asset)
    return new_asset

@app.patch("/api/v1/assets/{asset_id}")
async def update_asset(asset_id: str, asset_update: Dict[str, Any]):
    for i, asset in enumerate(mock_assets):
        if asset["id"] == asset_id:
            mock_assets[i] = {
                **asset,
                **asset_update,
                "updated_at": datetime.now().isoformat()
            }
            return mock_assets[i]
    raise HTTPException(status_code=404, detail="Asset not found")

# Shot endpoints
@app.get("/api/v1/shots/")
async def get_shots():
    return mock_shots

@app.get("/api/v1/shots/{shot_id}")
async def get_shot(shot_id: str):
    for shot in mock_shots:
        if shot["id"] == shot_id:
            return shot
    raise HTTPException(status_code=404, detail="Shot not found")

@app.post("/api/v1/shots/")
async def create_shot(shot: Dict[str, Any]):
    new_shot = {
        "id": f"shot-{str(uuid.uuid4())[:8]}",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        **shot
    }
    mock_shots.append(new_shot)
    return new_shot

@app.patch("/api/v1/shots/{shot_id}")
async def update_shot(shot_id: str, shot_update: Dict[str, Any]):
    for i, shot in enumerate(mock_shots):
        if shot["id"] == shot_id:
            mock_shots[i] = {
                **shot,
                **shot_update,
                "updated_at": datetime.now().isoformat()
            }
            return mock_shots[i]
    raise HTTPException(status_code=404, detail="Shot not found")

# For testing the API is running
@app.get("/")
async def root():
    return {"message": "Bifrost Mock API is running"}
