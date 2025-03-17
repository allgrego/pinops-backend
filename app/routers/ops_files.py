from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.database import SessionDep
from app.models.ops_files import OpsStatus, OpsStatusPublic, OpsStatusCreate, OpsStatusUpdate, OpsFile, OpsFilePublic, OpsFileCreate, OpsFileUpdate
from uuid import UUID

router = APIRouter(
    prefix="/ops",
    tags=["ops files"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)


"""
    Operations files status
"""

@router.get("/status", response_model=list[OpsStatusPublic]) 
def read_ops_statuses(db: SessionDep):
    ops_statuses = db.exec(select(OpsStatus)).all()
    return ops_statuses

@router.get("/status/{status_id}", response_model=OpsStatusPublic) 
def read_ops_status(status_id: int, db: SessionDep):
    ops_status = db.get(OpsStatus, status_id)
    if not ops_status:
        raise HTTPException(status_code=404, detail="Ops status not found")
    return ops_status


"""
    Operations files
"""

@router.get("/", response_model=list[OpsFilePublic]) 
def read_ops_files(db: SessionDep):
    ops_files = db.exec(select(OpsFile)).all()
    return ops_files

@router.post("/", response_model=OpsFilePublic)
def create_ops_file(ops_file: OpsFileCreate, db: SessionDep):
    db_ops_file = OpsFile.model_validate(ops_file)
    db.add(db_ops_file)
    db.commit()
    db.refresh(db_ops_file)
    return db_ops_file


@router.patch("/{ops_file_id}", response_model=OpsFilePublic)
def update_ops_file(ops_file_id: UUID, ops_file: OpsFileUpdate, db: SessionDep):
    ops_file_db = db.get(OpsFile, ops_file_id)
    if not ops_file_db:
        raise HTTPException(status_code=404, detail="Ops file not found")
    ops_file_data = ops_file.model_dump(exclude_unset=True)
    ops_file_db.sqlmodel_update(ops_file_data)
    db.add(ops_file_db)
    db.commit()
    db.refresh(ops_file_db)
    return ops_file_db

@router.delete("/{ops_file_id}")
def delete_ops_file(ops_file_id: UUID, db: SessionDep):
    ops_file = db.get(OpsFile, ops_file_id)
    if not ops_file:
        raise HTTPException(status_code=404, details="Ops File not found")
    db.delete(ops_file)
    db.commit()
    return {"ok": True}