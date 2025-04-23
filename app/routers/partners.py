from fastapi import APIRouter,  HTTPException
from sqlmodel import select, desc
from app.database import SessionDep
from app.models.partners import PartnerTypePublic, PartnerType, Partner, PartnerPublic, PartnerCreate, PartnerUpdate, PartnerContact, PartnerContactCreate, PartnerContactPublic, PartnerContactUpdate, PartnerContactCreateBase
from uuid import UUID
from typing import List

router = APIRouter(
    prefix="/partners",
    tags=["partners"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)

""" 
    Partner types routes
"""

@router.get("/types/", response_model=list[PartnerTypePublic]) 
def read_partner_types(db: SessionDep):
    partner_types = db.exec(select(PartnerType)).all()
    return partner_types

@router.get("/types/{partner_type_id}/", response_model=PartnerTypePublic)
def read_partner_type(partner_type_id: str, db: SessionDep):
    partner_type = db.get(PartnerType, partner_type_id)
    if not partner_type:
        raise HTTPException(status_code=404, detail="partner type not found")
    return partner_type

""" 
    Partner routes
"""

@router.post("/", response_model=PartnerPublic)
def create_partner(partner: PartnerCreate, db: SessionDep):
    db_partner = Partner.model_validate(partner)
    # Obtained generated partner ID
    partner_id = db_partner.partner_id
    # Iterate on each contact data
    for contact_data in partner.initial_contacts:
        # New contact instance
        db_contact = PartnerContact(
            partner_id=partner_id,
            name=contact_data.name, 
            position=contact_data.position, 
            email=contact_data.email, 
            phone=contact_data.phone, 
            mobile=contact_data.mobile,
        )
        db_partner.partner_contacts.append(db_contact)
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    return db_partner

@router.get("/", response_model=list[PartnerPublic]) 
def read_partners(db: SessionDep):
    partners = db.exec(select(Partner).order_by(desc(Partner.created_at))).all()
    return partners

@router.get("/{partner_id}/", response_model=PartnerPublic)
def read_partner(partner_id: UUID, db: SessionDep):
    partner = db.get(Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@router.patch("/{partner_id}/", response_model=PartnerPublic)
def update_partner(partner_id: UUID, partner: PartnerUpdate, db: SessionDep):
    partner_db = db.get(Partner, partner_id)
    if not partner_db:
        raise HTTPException(status_code=404, detail="partner not found")
    partner_data = partner.model_dump(exclude_unset=True)

    partner_db.sqlmodel_update(partner_data)

    provided_contacts = partner_data.get('partner_contacts')

    # Manage new contacts list if provided
    if provided_contacts is not None:
        # Reset current contacts list
        partner_db.partner_contacts.clear()
        
        # Iterate on new contacts list and Add contacts instances to partner instance
        for contact_obtained_data in provided_contacts:
            contact_data = PartnerContactCreateBase.model_validate(contact_obtained_data)
            # New contact instance
            db_contact = PartnerContact(
                partner_id=partner_id,
                name=contact_data.name, 
                position=contact_data.position, 
                email=contact_data.email, 
                phone=contact_data.phone, 
                mobile=contact_data.mobile,
            )
            partner_db.partner_contacts.append(db_contact)

    db.add(partner_db)
    db.commit()
    db.refresh(partner_db)
    return partner_db


@router.delete("/{partner_id}/")
def delete_partner(partner_id: UUID, db: SessionDep):
    partner = db.get(Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    db.delete(partner)
    db.commit()
    return {"ok": True} 


"""
    Partner contacts routes
"""

@router.post("/contacts", response_model=PartnerContactPublic)
def create_partner_contact(partner_contact: PartnerContactCreate, db: SessionDep):
    db_partner_contact = PartnerContact.model_validate(partner_contact)
    db.add(db_partner_contact)
    db.commit()
    db.refresh(db_partner_contact)
    return db_partner_contact

@router.get("/contacts", response_model=List[PartnerContactPublic]) 
def read_partners_contacts(db: SessionDep):
    partner_contacts = db.exec(select(PartnerContact).order_by(desc(PartnerContact.created_at))).all()
    return partner_contacts

@router.get("/contacts/{contact_id}/", response_model=PartnerContactPublic)
def read_partner_contact(contact_id: UUID, db: SessionDep):
    partner_contact = db.get(PartnerContact, contact_id)
    if not partner_contact:
        raise HTTPException(status_code=404, detail="Partner contact not found")
    return partner_contact

@router.get("/contacts/partner/{partner_id}/", response_model=List[PartnerContactPublic])
def read_partner_contacts_by_partner(partner_id: UUID, db: SessionDep):   
    partner = db.get(Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    partner_contacts = db.exec(
        select(PartnerContact)
        .where(PartnerContact.partner_id == partner_id)
        .order_by(desc(PartnerContact.created_at))
    ).all()
    return partner_contacts

@router.patch("/contacts/{contact_id}/", response_model=PartnerContactPublic)
def update_partner_contact(contact_id: UUID, partner_contact: PartnerContactUpdate, db: SessionDep):
    partner_contact_db = db.get(PartnerContact, contact_id)
    if not partner_contact_db:
        raise HTTPException(status_code=404, detail="partner contact not found")
    partner_contact_data = partner_contact.model_dump(exclude_unset=True)
    partner_contact_db.sqlmodel_update(partner_contact_data)
    db.add(partner_contact_db)
    db.commit()
    db.refresh(partner_contact_db)
    return partner_contact_db


@router.delete("/contacts/{contact_id}/")
def delete_partner_contact(contact_id: UUID, db: SessionDep):
    partner_contact = db.get(PartnerContact, contact_id)
    if not partner_contact:
        raise HTTPException(status_code=404, detail="partner contact not found")
    db.delete(partner_contact)
    db.commit()
    return {"ok": True} 
