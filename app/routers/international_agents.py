from fastapi import APIRouter, HTTPException
from sqlmodel import select, desc
from app.database import SessionDep
from app.models.international_agents import InternationalAgent, InternationalAgentCreate, InternationalAgentPublic, InternationalAgentUpdate
from uuid import UUID

router = APIRouter(
    prefix="/agents",
    tags=["international agents"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)

""" 
    International Agents
"""

@router.post("/", response_model=InternationalAgentPublic)
def create_International_agent(international_agent: InternationalAgentCreate, db: SessionDep):
    db_International_agent = InternationalAgent.model_validate(international_agent)
    db.add(db_International_agent)
    db.commit()
    db.refresh(db_International_agent)
    return db_International_agent

@router.get("/", response_model=list[InternationalAgentPublic]) 
def read_international_agents(db: SessionDep):
    international_agents = db.exec(select(InternationalAgent).order_by(desc(InternationalAgent.created_at))).all()
    return international_agents

@router.get("/{international_agent_id}", response_model=InternationalAgentPublic)
def read_international_agent(international_agent_id: UUID, db: SessionDep):
    international_agent = db.get(InternationalAgent, international_agent_id)
    if not international_agent:
        raise HTTPException(status_code=404, detail="International agent not found")
    return international_agent


@router.patch("/{international_agent_id}", response_model=InternationalAgentPublic)
def update_international_agent(international_agent_id: UUID, international_agent: InternationalAgentUpdate, db: SessionDep):
    international_agent_db = db.get(InternationalAgent, international_agent_id)
    if not international_agent_db:
        raise HTTPException(status_code=404, detail="International agent not found")
    international_agent_data = international_agent.model_dump(exclude_unset=True)
    international_agent_db.sqlmodel_update(international_agent_data)
    db.add(international_agent_db)
    db.commit()
    db.refresh(international_agent_db)
    return international_agent_db


@router.delete("/{international_agent_id}")
def delete_international_agent(international_agent_id: UUID, db: SessionDep):
    international_agent = db.get(InternationalAgent, international_agent_id)
    if not international_agent:
        raise HTTPException(status_code=404, detail="International agent not found")
    db.delete(international_agent)
    db.commit()
    return {"ok": True}