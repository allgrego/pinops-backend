from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4

SCHEMA_NAME = 'providers'

"""
    International Agents
"""

class InternationalAgentBase(SQLModel):
    name: str = Field(default=None)

class InternationalAgent(InternationalAgentBase, table=True):
    __tablename__ = "international_agents"
    __table_args__ = {"schema": SCHEMA_NAME}

    agent_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "agent_id"})

    ops_files: Optional[List["OpsFile"]] = Relationship(back_populates="agent")
    
class InternationalAgentPublic(InternationalAgentBase):
    agent_id: UUID

class InternationalAgentCreate(InternationalAgentBase):
    name: str

class InternationalAgentUpdate(InternationalAgentBase):
    name: str

