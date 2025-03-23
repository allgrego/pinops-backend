from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from app.models.ops_files_int_agents import OpsFileInternationalAgentLink

SCHEMA_NAME = 'providers'

"""
    International Agents
"""

class InternationalAgentBase(SQLModel):
    name: str = Field(unique=True)
    tax_id: Optional[str] = Field(default=None, max_length=100, unique=True)
    contact_name: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=100)
    contact_email: Optional[str] = Field(default=None, max_length=255)

class InternationalAgent(InternationalAgentBase, table=True):
    __tablename__ = "international_agents"
    __table_args__ = {"schema": SCHEMA_NAME}

    agent_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "agent_id"})

    ops_files: Optional[List["OpsFile"]] = Relationship(back_populates="agents", link_model=OpsFileInternationalAgentLink)
    
class InternationalAgentPublic(InternationalAgentBase):
    agent_id: UUID

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class InternationalAgentCreate(InternationalAgentBase):
    pass

class InternationalAgentUpdate(InternationalAgentBase):
    name: Optional[str] = None

