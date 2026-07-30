# routers/stores.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

router = APIRouter(prefix="/stores", tags=["Stores"])

@router.post("/", response_model=schemas.StoreResponse)
def create_store(store: schemas.StoreCreate, db: Session = Depends(get_db)):
    db_store = models.StoreModel(name=store.name, city=store.city)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

@router.get("/", response_model=List[schemas.StoreResponse])
def get_stores(db: Session = Depends(get_db)):
    return db.query(models.StoreModel).all()