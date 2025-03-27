from fastapi import APIRouter,  HTTPException
from sqlmodel import select, desc
from app.database import SessionDep
from app.models.clients import Client, ClientPublic, ClientCreate, ClientUpdate
from uuid import UUID

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ClientPublic)
def create_client(client: ClientCreate, db: SessionDep):
    db_client = Client.model_validate(client)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/", response_model=list[ClientPublic]) 
def read_clients(db: SessionDep):
    clients = db.exec(select(Client).order_by(desc(Client.created_at))).all()
    return clients

@router.get("/{client_id}", response_model=ClientPublic)
def read_client(client_id: UUID, db: SessionDep):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientPublic)
def update_client(client_id: UUID, client: ClientUpdate, db: SessionDep):
    client_db = db.get(Client, client_id)
    if not client_db:
        raise HTTPException(status_code=404, detail="Client not found")
    client_data = client.model_dump(exclude_unset=True)
    client_db.sqlmodel_update(client_data)
    db.add(client_db)
    db.commit()
    db.refresh(client_db)
    return client_db


@router.delete("/{client_id}")
def delete_client(client_id: UUID, db: SessionDep):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"ok": True} 