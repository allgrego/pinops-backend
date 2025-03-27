from fastapi import APIRouter, HTTPException
from sqlmodel import select, desc
from app.database import SessionDep
from app.models.carriers import Carrier, CarrierCreate, CarrierPublic, CarrierUpdate
from uuid import UUID

router = APIRouter(
    prefix="/carriers",
    tags=["carriers"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)

""" 
    Carriers
"""

@router.post("/", response_model=CarrierPublic)
def create_carrier(carrier: CarrierCreate, db: SessionDep):
    db_carrier = Carrier.model_validate(carrier)
    db.add(db_carrier)
    db.commit()
    db.refresh(db_carrier)
    return db_carrier

@router.get("/", response_model=list[CarrierPublic]) 
def read_carriers(db: SessionDep):
    carriers = db.exec(select(Carrier).order_by(desc(Carrier.created_at))).all()
    return carriers

@router.get("/{carrier_id}", response_model=CarrierPublic)
def read_carrier(carrier_id: UUID, db: SessionDep):
    carrier = db.get(Carrier, carrier_id)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return carrier

@router.patch("/{carrier_id}", response_model=CarrierPublic)
def update_carrier(carrier_id: UUID, carrier: CarrierUpdate, db: SessionDep):
    carrier_db = db.get(Carrier, carrier_id)
    if not carrier_db:
        raise HTTPException(status_code=404, detail="Carrier not found")
    carrier_data = carrier.model_dump(exclude_unset=True)
    carrier_db.sqlmodel_update(carrier_data)
    db.add(carrier_db)
    db.commit()
    db.refresh(carrier_db)
    return carrier_db

@router.delete("/{carrier_id}")
def delete_carrier(carrier_id: UUID, db: SessionDep):
    carrier = db.get(Carrier, carrier_id)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    db.delete(carrier)
    db.commit()
    return {"ok": True}