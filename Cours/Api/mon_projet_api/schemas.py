# schemas.py
from pydantic import BaseModel
from typing import Optional

# --- SCHÉMAS ITEM ---
class ItemCreate(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = False

class ItemResponse(ItemCreate):
    id: int
    class Config:
        from_attributes = True

# --- SCHÉMAS USER (Nouveau !) ---
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(UserCreate):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

# --- SCHÉMAS STORE (Nouveau !) ---
class StoreCreate(BaseModel):
    name: str
    city: str

class StoreResponse(StoreCreate):
    id: int
    class Config:
        from_attributes = True