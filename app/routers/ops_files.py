from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.database import SessionDep
from app.models.international_agents import InternationalAgent
from app.models.ops_files import OpsStatus, OpsStatusPublic, OpsFile, OpsFilePublic, OpsFileCreate, OpsFileUpdate, OpsFileComment, OpsFileCommentPublic, OpsFileCommentCreate, OpsFileCommentUpdate
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
    
    # Add agents instances to Ops File instance
    for agent_id in ops_file.agents_id:
        db_agent = db.get(InternationalAgent, agent_id)
        if not db_agent:
            raise HTTPException(status_code=404, detail=f"Agent not found. ID: {agent_id}")
        
        db_ops_file.agents.append(db_agent)
        
    db.add(db_ops_file)
    db.commit()
    db.refresh(db_ops_file)
    return db_ops_file

@router.get("/", response_model=list[OpsFilePublic]) 
def read_ops_files(db: SessionDep):
    ops_files = db.exec(select(OpsFile)).all()
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
    
    # Manage new agents list if provided
    if ops_file_data.get('agents_id') is not None:
        
        # Reset current agents list
        ops_file_db.agents.clear()
        
        # Iterate on new agents list and Add agents instances to Ops File instance
        for agent_id in ops_file.agents_id:
            db_agent = db.get(InternationalAgent, agent_id)
             
            if not db_agent:
                raise HTTPException(status_code=404, detail=f"Agent not found for ID {agent_id}")
        
            ops_file_db.agents.append(db_agent)

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

@router.get("/comments/{comment_id}", response_model=OpsFileCommentPublic)
def read_ops_file_comment(comment_id: UUID, db: SessionDep):
    comment_db = db.get(OpsFileComment, comment_id)
    if not comment_db:
        raise HTTPException(status_code=404, detail="Comment not found")   
    return comment_db

@router.patch("/comments/{comment_id}", response_model=OpsFileCommentPublic) 
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

@router.delete("/comments/{comment_id}") 
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

@router.get("/status/{status_id}", response_model=OpsStatusPublic) 
def read_ops_status(status_id: int, db: SessionDep):
    ops_status = db.get(OpsStatus, status_id)
    if not ops_status:
        raise HTTPException(status_code=404, detail="Ops status not found")
    return ops_status
