from fastapi import APIRouter, HTTPException
from sqlmodel import select, func, desc
from app.database import SessionDep
from app.models.partners import Partner
from app.models.ops_files import OpsStatus, OpsStatusPublic, OpsFile, OpsFilePublic, OpsFileCreate, OpsFileUpdate, OpsFileComment, OpsFileCommentPublic, OpsFileCommentCreate, OpsFileCommentUpdate, OpsFileCargoPackage, OpsFileCargoPackageCreateWithoutOpId, OpsFileCommentBase
from app.models.carriers import Carrier
from app.models.clients import Client
from uuid import UUID

router = APIRouter(
    prefix="/ops",
    tags=["ops files"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)


"""
    Operations files
"""

@router.post("/", response_model=OpsFilePublic)
def create_ops_file(ops_file: OpsFileCreate, db: SessionDep):
    db_ops_file = OpsFile.model_validate(ops_file)
    
    # Add partners instances to Ops File instance
    for partner_id in ops_file.partners_id:
        db_partner = db.get(Partner, partner_id)
        if not db_partner:
            raise HTTPException(status_code=404, detail=f"Partner not found. Invalid ID: {partner_id}")
        
        db_ops_file.partners.append(db_partner)

    ops_file_id = db_ops_file.op_id
    creator_user_id = db_ops_file.creator_user_id

    # Add packaging instances to ops file instance
    for package_data in ops_file.packaging_data:
        packaging_data = OpsFileCargoPackageCreateWithoutOpId.model_validate(package_data)
        # Create package instance
        db_package = OpsFileCargoPackage(op_id=ops_file_id, quantity=packaging_data.quantity, units=packaging_data.units)
        # Associate it with ops file
        db_ops_file.packaging.append(db_package)

    # Add comment if any (the creator is the author)
    if ops_file.comment is not None: 
        comment_data = OpsFileCommentBase.model_validate(ops_file.comment)
        db_comment = OpsFileComment(author_user_id=creator_user_id, content=comment_data.content, op_id=ops_file_id)
        db_ops_file.comments.append(db_comment)

    db.add(db_ops_file)
    db.commit()
    db.refresh(db_ops_file)
    return db_ops_file

@router.get("/", response_model=list[OpsFilePublic]) 
def read_ops_files(db: SessionDep):
    ops_files = db.exec(select(OpsFile).order_by(desc(OpsFile.created_at))).all()
    return ops_files

@router.get("/{ops_file_id}", response_model=OpsFilePublic) 
def read_ops_file(ops_file_id: UUID, db: SessionDep):
    ops_file_db = db.get(OpsFile, ops_file_id)
    if not ops_file_db:
        raise HTTPException(status_code=404, detail="Ops file not found")   

    return ops_file_db

@router.patch("/{ops_file_id}", response_model=OpsFilePublic)
def update_ops_file(ops_file_id: UUID, ops_file: OpsFileUpdate, db: SessionDep):
    ops_file_db = db.get(OpsFile, ops_file_id)
    if not ops_file_db:
        raise HTTPException(status_code=404, detail="Ops file not found")
    ops_file_data = ops_file.model_dump(exclude_unset=True)
    ops_file_db.sqlmodel_update(ops_file_data)
    
    # Manage new partners list if provided
    if ops_file_data.get('partners_id') is not None:
        # Reset current partners list
        ops_file_db.partners.clear()
        
        # Iterate on new partners list and Add partners instances to Ops File instance
        for partner_id in ops_file.partners_id:
            db_partner = db.get(Partner, partner_id)
             
            if not db_partner:
                raise HTTPException(status_code=404, detail=f"Partner not found for ID {partner_id}")
        
            ops_file_db.partners.append(db_partner)

    # Manage new packaging list if provided
    if ops_file_data.get('packaging_data') is not None:
        # Reset current partners list
        ops_file_db.packaging.clear()
        
        # Iterate on new partners list and Add partners instances to Ops File instance
        for package_data in ops_file.packaging_data:
            packaging_data = OpsFileCargoPackageCreateWithoutOpId.model_validate(package_data)
            # Create package instance
            db_package = OpsFileCargoPackage(
                op_id=ops_file_id, 
                quantity=packaging_data.quantity, 
                units=packaging_data.units
            )
            # Associate it with ops file            
            ops_file_db.packaging.append(db_package)

    db.add(ops_file_db)
    db.commit()
    db.refresh(ops_file_db)
    return ops_file_db

@router.delete("/{ops_file_id}")
def delete_ops_file(ops_file_id: UUID, db: SessionDep):
    ops_file = db.get(OpsFile, ops_file_id)
    if not ops_file:
        raise HTTPException(status_code=404, detail="Ops File not found")
    db.delete(ops_file)
    db.commit()
    return {"ok": True}

"""
    Operations files comments
"""

@router.post("/comments", response_model=OpsFileCommentPublic) 
def create_ops_file_comment(comment: OpsFileCommentCreate, db: SessionDep):
    
    comment_db = OpsFileComment.model_validate(comment)
    
    ops_file_db = db.get(OpsFile, comment_db.op_id)

    if not ops_file_db:
        raise HTTPException(status_code=404, detail="Ops file not found")   

    db.add(comment_db)
    db.commit()
    db.refresh(ops_file_db)
    return comment_db

@router.get("/comments/{comment_id}/", response_model=OpsFileCommentPublic)
def read_ops_file_comment(comment_id: UUID, db: SessionDep):
    comment_db = db.get(OpsFileComment, comment_id)
    if not comment_db:
        raise HTTPException(status_code=404, detail="Comment not found")   
    return comment_db

@router.patch("/comments/{comment_id}/", response_model=OpsFileCommentPublic) 
def update_ops_file_comment(comment_id: UUID, comment: OpsFileCommentUpdate, db: SessionDep):

    comment_db = db.get(OpsFileComment, comment_id)

    if not comment_db:
        raise HTTPException(status_code=404, detail="Comment not found")   

    comment_data = comment.model_dump(exclude_unset=True)
    comment_db.sqlmodel_update(comment_data)

    db.add(comment_db)
    db.commit()
    db.refresh(comment_db)

    return comment_db

@router.delete("/comments/{comment_id}/") 
def delete_ops_file_comment(comment_id: UUID, db: SessionDep):
    comment_db = db.get(OpsFileComment, comment_id)

    if not comment_db:
        raise HTTPException(status_code=404, detail="Comment not found")   
    
    db.delete(comment_db)
    db.commit()
    return {"ok": True}


"""
    Operations files status
"""

@router.get("/status", response_model=list[OpsStatusPublic]) 
def read_ops_statuses(db: SessionDep):
    ops_statuses = db.exec(select(OpsStatus)).all()
    return ops_statuses

@router.get("/status/{status_id}/", response_model=OpsStatusPublic) 
def read_ops_status(status_id: int, db: SessionDep):
    ops_status = db.get(OpsStatus, status_id)
    if not ops_status:
        raise HTTPException(status_code=404, detail="Ops status not found")
    return ops_status

"""
    Stats

    TODO: Move to other namespace
"""


@router.get("/general/statistics/") 
def read_ops_statistics(db: SessionDep):
    clients_count = db.exec(select(func.count(Client.client_id))).one() 
    carriers_count = db.exec(select(func.count(Carrier.carrier_id))).one()
    partners_count = db.exec(select(func.count(Partner.partner_id))).one()
    ops_files_count = db.exec(select(func.count(OpsFile.op_id))).one()
    closed_status_id = 0
    closed_ops_files_count = db.exec(select(func.count(OpsFile.op_id)).where(OpsFile.status_id != closed_status_id)).one()
    
    return {
        "total_clients": clients_count,
        "total_partners": partners_count,
        "total_carriers": carriers_count,
        "total_ops_files": ops_files_count,
        "total_closed_ops_files": closed_ops_files_count,
        "total_open_ops_files": ops_files_count - closed_ops_files_count
    }