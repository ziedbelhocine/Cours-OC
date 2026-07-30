# routers/items.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/")
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.ItemModel(name=item.name, price=item.price, is_offer=item.is_offer)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[schemas.ItemResponse])
def get_items(db: Session = Depends(get_db)):
    return db.query(models.ItemModel).all()