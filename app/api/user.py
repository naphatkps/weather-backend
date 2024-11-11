from fastapi import APIRouter
from app.database import db
from app.models.user import UserRequest, UserBase, UserResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


router = APIRouter()
collection = db['users']

def convert_object_id(item):
    """Convert ObjectId fields to strings in a MongoDB document."""
    if isinstance(item, list):
        for doc in item:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
    elif item and "_id" in item:
        item["_id"] = str(item["_id"])
    return item

@router.post("/users/", response_model=UserBase)
async def create_user(user: UserRequest):
    user_data = jsonable_encoder(user)
    if collection.find_one({"email": user_data["email"]}):
        return JSONResponse(
            content={"error": "Email already exists"},
            status_code=400
        )
    result = collection.insert_one(user_data)
    created_user = collection.find_one({"_id": result.inserted_id})
    created_user = convert_object_id(created_user)
    return JSONResponse(content=created_user)

@router.get("/users/", response_model=list[UserResponse])
async def get_users():
    users = list(collection.find({}, {"email": 1, "_id": 0}))
    return JSONResponse(content=users)
    
    