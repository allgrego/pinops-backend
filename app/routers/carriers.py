from fastapi import APIRouter,  HTTPException
from sqlmodel import select, desc
from app.database import SessionDep
from app.models.carriers import CarrierTypePublic, CarrierType, Carrier, CarrierPublic, CarrierCreate, CarrierUpdate, CarrierContact  , CarrierContactCreate, CarrierContactPublic, CarrierContactUpdate, CarrierContactCreateBase
from uuid import UUID
from typing import List

router = APIRouter(
    prefix="/carriers",
    tags=["carriers"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)

""" 
    Carrier types routes
"""

@router.get("/types", response_model=List[CarrierTypePublic]) 
def read_carrier_types(db: SessionDep):
    carrier_types = db.exec(select(CarrierType)).all()
    return carrier_types

@router.get("/types/{carrier_type_id}/", response_model=CarrierTypePublic)
def read_carrier_type(carrier_type_id: str, db: SessionDep):
    carrier_type = db.get(CarrierType, carrier_type_id)
    if not carrier_type:
        raise HTTPException(status_code=404, detail="Carrier type not found")
    return carrier_type

""" 
    Carrier routes
"""

@router.post("/", response_model=CarrierPublic)
def create_carrier(carrier: CarrierCreate, db: SessionDep):
    db_carrier = Carrier.model_validate(carrier)
    # Obtained generated carrier ID
    carrier_id = db_carrier.carrier_id
    # Iterate on each contact data
    for contact_data in carrier.initial_contacts:
        # New contact instance
        db_contact = CarrierContact(
            carrier_id=carrier_id,
            name=contact_data.name, 
            position=contact_data.position, 
            email=contact_data.email, 
            phone=contact_data.phone, 
            mobile=contact_data.mobile,
        )
        db_carrier.carrier_contacts.append(db_contact)
    db.add(db_carrier)
    db.commit()
    db.refresh(db_carrier)
    return db_carrier

@router.get("/", response_model=List[CarrierPublic]) 
def read_carriers(db: SessionDep):
    carriers = db.exec(select(Carrier).order_by(desc(Carrier.created_at))).all()
    return carriers

@router.get("/{carrier_id}/", response_model=CarrierPublic)
def read_carrier(carrier_id: UUID, db: SessionDep):
    carrier = db.get(Carrier, carrier_id)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return carrier


@router.patch("/{carrier_id}/", response_model=CarrierPublic)
def update_carrier(carrier_id: UUID, carrier: CarrierUpdate, db: SessionDep):
    carrier_db = db.get(Carrier, carrier_id)
    if not carrier_db:
        raise HTTPException(status_code=404, detail="Carrier not found")
    carrier_data = carrier.model_dump(exclude_unset=True)
    carrier_db.sqlmodel_update(carrier_data)
    
    provided_contacts = carrier_data.get('carrier_contacts')
    # Manage new contacts list if provided
    if provided_contacts is not None:
        # Reset current contacts list
        carrier_db.carrier_contacts.clear()
        
        # Iterate on new contacts list and Add contacts instances to carrier instance
        for contact_obtained_data in provided_contacts:
            contact_data = CarrierContactCreateBase.model_validate(contact_obtained_data)
            # New contact instance
            db_contact = CarrierContact(
                carrier_id=carrier_id,
                name=contact_data.name, 
                position=contact_data.position, 
                email=contact_data.email, 
                phone=contact_data.phone, 
                mobile=contact_data.mobile,
            )
            carrier_db.carrier_contacts.append(db_contact)
    db.add(carrier_db)
    db.commit()
    db.refresh(carrier_db)
    return carrier_db


@router.delete("/{carrier_id}/")
def delete_carrier(carrier_id: UUID, db: SessionDep):
    carrier = db.get(Carrier, carrier_id)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    db.delete(carrier)
    db.commit()
    return {"ok": True} 


"""
    carrier contacts routes
"""

@router.post("/contacts", response_model=CarrierContactPublic)
def create_carrier_contact(carrier_contact: CarrierContactCreate, db: SessionDep):
    db_carrier_contact = CarrierContact.model_validate(carrier_contact)
    db.add(db_carrier_contact)
    db.commit()
    db.refresh(db_carrier_contact)
    return db_carrier_contact

@router.get("/contacts", response_model=List[CarrierContactPublic]) 
def read_carriers_contacts(db: SessionDep):
    carrier_contacts = db.exec(select(CarrierContact).order_by(desc(CarrierContact.created_at))).all()
    return carrier_contacts

@router.get("/contacts/{contact_id}/", response_model=CarrierContactPublic)
def read_carrier_contact(contact_id: UUID, db: SessionDep):
    carrier_contact = db.get(CarrierContact, contact_id)
    if not carrier_contact:
        raise HTTPException(status_code=404, detail="Carrier contact not found")
    return carrier_contact

@router.get("/contacts/carrier/{carrier_id}/", response_model=List[CarrierContactPublic])
def read_carrier_contacts_by_carrier(carrier_id: UUID, db: SessionDep):   
    carrier = db.get(Carrier, carrier_id)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    carrier_contacts = db.exec(
        select(CarrierContact)
        .where(CarrierContact.carrier_id == carrier_id)
        .order_by(desc(CarrierContact.created_at))
    ).all()
    return carrier_contacts

@router.patch("/contacts/{contact_id}/", response_model=CarrierContactPublic)
def update_carrier_contact(contact_id: UUID, carrier_contact: CarrierContactUpdate, db: SessionDep):
    carrier_contact_db = db.get(CarrierContact, contact_id)
    if not carrier_contact_db:
        raise HTTPException(status_code=404, detail="Carrier contact not found")
    carrier_contact_data = carrier_contact.model_dump(exclude_unset=True)
    carrier_contact_db.sqlmodel_update(carrier_contact_data)
    db.add(carrier_contact_db)
    db.commit()
    db.refresh(carrier_contact_db)
    return carrier_contact_db


@router.delete("/contacts/{contact_id}/")
def delete_carrier_contact(contact_id: UUID, db: SessionDep):
    carrier_contact = db.get(CarrierContact, contact_id)
    if not carrier_contact:
        raise HTTPException(status_code=404, detail="Carrier contact not found")
    db.delete(carrier_contact)
    db.commit()
    return {"ok": True} 
