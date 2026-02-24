"""
Players router.
Handles player CRUD operations, image upload, and public registration.
"""
from fastapi import APIRouter, HTTPException, Depends, Form, Query, File, UploadFile
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
import os
import uuid
from pathlib import Path

from database import db
from core.security import get_current_user, require_admin
from core.config import settings
from core.cloudinary_config import upload_image, delete_image, is_cloudinary_configured
from schemas.player import (
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
    PlayerPublicRegister,
    SetBasePriceRequest
)

router = APIRouter(prefix="/players", tags=["Players"])

# Ensure upload directory exists (fallback for local storage)
UPLOAD_DIR = Path("static/uploads/players")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def serialize_player(doc: dict) -> dict:
    """Convert MongoDB document to API response format."""
    # Convert ObjectId to string
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    
    # Convert any other ObjectId fields to strings
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    
    # Get team name if player is assigned
    team_id = doc.get("final_team") or doc.get("current_team")
    if team_id:
        try:
            if isinstance(team_id, str):
                team = db.teams.find_one({"_id": ObjectId(team_id)})
            else:
                team = db.teams.find_one({"_id": team_id})
            if team:
                doc["team_name"] = team.get("name")
        except Exception:
            pass
    
    return doc


@router.post("/upload-image/{player_id}")
async def upload_player_image(
    player_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload player image to Cloudinary or local storage."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WebP are allowed."
        )
    
    # Validate file size (5MB max)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")
    
    try:
        pid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    player = db.players.find_one({"_id": pid})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    image_url = None
    
    # Try Cloudinary first, fallback to local storage
    if is_cloudinary_configured():
        # Upload to Cloudinary
        result = upload_image(contents, file.filename)
        if result.get("success"):
            image_url = result.get("url")
        else:
            raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {result.get('error')}")
    else:
        # Fallback to local storage
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{player_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        image_url = f"/static/uploads/players/{unique_filename}"
    
    # Update player with image path
    db.players.update_one(
        {"_id": pid},
        {"$set": {"image_path": image_url, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"ok": True, "image_path": image_url}


@router.post("/public_register")
async def public_player_register(
    full_name: str = Form(...),
    role: str = Form(...),  # Playing position (Batsman, Bowler, etc.)
    category: Optional[str] = Form(None),  # Affiliation (Faculty, Student, Alumni)
    base_price: int = Form(...),  # MANDATORY manual base price
    age: Optional[int] = Form(None),
    batting_style: Optional[str] = Form(None),
    bowling_style: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    photo: UploadFile = File(...),  # MANDATORY photo upload
    # ML Prediction fields
    matches_played: int = Form(0),
    batting_average: float = Form(25.0),
    strike_rate: float = Form(120.0),
    wickets: int = Form(10),
    economy_rate: float = Form(8.0),
    recent_performance_score: float = Form(70.0)
):
    """Public endpoint for player self-registration with MANDATORY image and manual base price - AUTO-APPROVED."""
    name = (full_name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Full name is required")
    
    # Validate base price
    if not base_price or base_price < 10000:
        raise HTTPException(
            status_code=400,
            detail="Base price must be at least ₹10,000"
        )
    
    # Check for duplicate player by name (case-insensitive)
    existing_player = db.players.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if existing_player:
        raise HTTPException(
            status_code=400, 
            detail=f"A player with the name '{name}' is already registered. Please use a different name or contact admin."
        )
    
    # Validate role (playing position)
    allowed_roles = {"Batsman", "Bowler", "All-Rounder", "Wicketkeeper"}
    if not role or role not in allowed_roles:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role. Must be one of: {', '.join(sorted(allowed_roles))}"
        )
    
    # Validate category (affiliation) - optional
    allowed_categories = {"Faculty", "Student", "Alumni"}
    if category and category not in allowed_categories:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid category. Must be one of: {', '.join(sorted(allowed_categories))}"
        )
    
    # MANDATORY photo validation
    if not photo or not photo.filename:
        raise HTTPException(status_code=400, detail="Profile photo is required for registration")
    
    # Validate image type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if photo.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Invalid image type. Only JPG, PNG, and WebP are allowed."
        )
    
    # Read file contents
    contents = await photo.read()
    
    # Validate file size (500KB max)
    max_size = 500 * 1024  # 500KB
    if len(contents) > max_size:
        actual_size_kb = len(contents) / 1024
        raise HTTPException(
            status_code=400, 
            detail=f"Photo size must be less than 500KB. Your photo is {actual_size_kb:.0f}KB. Please compress or choose a smaller photo."
        )
    
    image_path = None
    cloudinary_status = "not_attempted"
    
    # Try Cloudinary first, fallback to local storage
    if is_cloudinary_configured():
        print(f"📤 Uploading to Cloudinary: {photo.filename}")
        cloudinary_status = "configured"
        result = upload_image(contents, photo.filename)
        if result.get("success"):
            image_path = result.get("url")
            cloudinary_status = "success"
            print(f"✅ Cloudinary upload successful: {image_path}")
        else:
            cloudinary_status = f"failed: {result.get('error')}"
            print(f"❌ Cloudinary upload failed: {result.get('error')}")
            # Don't fallback to local - Railway filesystem is ephemeral
            print(f"⚠️ Image not saved - Cloudinary required for Railway deployment")
    else:
        # Fallback to local storage for development
        cloudinary_status = "not_configured"
        print(f"⚠️ Cloudinary not configured - saving to local storage")
        
        file_ext = photo.filename.split(".")[-1]
        unique_filename = f"player_{uuid.uuid4().hex}.{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        image_path = f"/static/uploads/players/{unique_filename}"
        print(f"✅ Image saved locally: {image_path}")
    
    player_doc = {
        "name": name,
        "role": role,
        "category": category or None,
        "age": age,
        "batting_style": (batting_style or "").strip(),
        "bowling_style": (bowling_style or "").strip(),
        "bio": (bio or "").strip(),
        "image_path": image_path,
        "base_price": base_price,  # Use manual base price from form
        "base_price_status": "approved",  # Auto-approved
        "status": "available",
        "is_approved": True,  # AUTO-APPROVED - No admin approval needed
        "is_live": False,
        "auction_round": 1,
        "current_team": None,
        "final_team": None,
        "final_bid": None,
        "created_by": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        # ML Prediction fields
        "matches_played": matches_played,
        "batting_average": batting_average,
        "strike_rate": strike_rate,
        "wickets": wickets,
        "economy_rate": economy_rate,
        "recent_performance_score": recent_performance_score
    }
    
    result = db.players.insert_one(player_doc)
    
    return {
        "ok": True,
        "player_id": str(result.inserted_id),
        "message": f"Registration successful! You are now available for auction with base price ₹{base_price:,}.",
        "base_price": base_price
    }


@router.post("/add")
async def add_player(
    player: PlayerCreate,
    current_user: dict = Depends(require_admin)
):
    """Add a new player (Admin only)."""
    player_doc = player.dict()
    player_doc.update({
        "status": "available",
        "base_price_status": "set" if player.base_price else "pending",
        "auction_round": 1,
        "current_team": None,
        "final_team": None,
        "final_bid": None,
        "created_by": current_user["user_id"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    
    result = db.players.insert_one(player_doc)
    
    return {"ok": True, "id": str(result.inserted_id)}


@router.get("/")
async def list_players(
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    auction_round: Optional[int] = Query(None),
    include_unapproved: bool = Query(True)  # Changed default to True - show all players
):
    """List all players with optional filters and pagination.
    Shows all players by default (approved and unapproved)."""
    query = {}
    
    # Filter by approval status (now shows all by default)
    if not include_unapproved:
        query["is_approved"] = True
    
    if status:
        query["status"] = status
    
    if role:
        query["role"] = role
    
    if category:
        query["category"] = category
    
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    if auction_round:
        query["auction_round"] = auction_round
    
    # Calculate skip for pagination
    skip = (page - 1) * limit
    
    # Get total count
    total = db.players.count_documents(query)
    
    # Get players with pagination, sorted by role then name
    players = [
        serialize_player(p) 
        for p in db.players.find(query).skip(skip).limit(limit).sort([("role", 1), ("name", 1)])
    ]
    
    return {
        "players": players,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/grouped/by-role")
async def get_players_grouped_by_role():
    """Get all players grouped by their role (Batsman, Bowler, etc.)."""
    roles = ["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"]
    grouped = {}
    
    for role in roles:
        players = [
            serialize_player(p)
            for p in db.players.find({"role": role, "is_approved": True}).sort("name", 1)
        ]
        grouped[role] = {
            "count": len(players),
            "players": players
        }
    
    # Get players with no role or other roles
    other_players = [
        serialize_player(p)
        for p in db.players.find({"role": {"$nin": roles}, "is_approved": True}).sort("name", 1)
    ]
    if other_players:
        grouped["Other"] = {
            "count": len(other_players),
            "players": other_players
        }
    
    return {
        "ok": True,
        "grouped": grouped,
        "total": sum(g["count"] for g in grouped.values())
    }


@router.get("/grouped/by-category")
async def get_players_grouped_by_category():
    """Get all players grouped by their category (Faculty, Student, Alumni)."""
    categories = ["Faculty", "Student", "Alumni"]
    grouped = {}
    
    for category in categories:
        players = [
            serialize_player(p)
            for p in db.players.find({"category": category, "is_approved": True}).sort("name", 1)
        ]
        grouped[category] = {
            "count": len(players),
            "players": players
        }
    
    # Get players with no category
    no_category = [
        serialize_player(p)
        for p in db.players.find({"category": None, "is_approved": True}).sort("name", 1)
    ]
    if no_category:
        grouped["Uncategorized"] = {
            "count": len(no_category),
            "players": no_category
        }
    
    return {
        "ok": True,
        "grouped": grouped,
        "total": sum(g["count"] for g in grouped.values())
    }


@router.get("/{player_id}")
async def get_player(player_id: str):
    """Get a specific player by ID."""
    try:
        player = db.players.find_one({"_id": ObjectId(player_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return serialize_player(player)


@router.put("/update/{player_id}")
async def update_player(
    player_id: str,
    player: PlayerUpdate,
    current_user: dict = Depends(require_admin)
):
    """Update a player (Admin only)."""
    try:
        pid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    update_data = {k: v for k, v in player.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = db.players.update_one(
        {"_id": pid},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {"ok": True, "message": "Player updated"}


@router.delete("/delete/{player_id}")
async def delete_player(
    player_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a player (Admin only)."""
    try:
        pid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    # Get player to delete image if exists
    player = db.players.find_one({"_id": pid})
    if player and player.get("image_path"):
        try:
            image_file = Path("static" + player["image_path"].replace("/static", ""))
            if image_file.exists():
                image_file.unlink()
        except Exception:
            pass
    
    result = db.players.delete_one({"_id": pid})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {"ok": True, "message": "Player deleted"}
