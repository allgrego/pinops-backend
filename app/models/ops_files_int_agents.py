
from sqlmodel import SQLModel, Field
from uuid import UUID

SCHEMA_NAME = 'ops'

"""
    Agents/Ops files link (many-to-many relationship)
"""

class OpsFileInternationalAgentLink(SQLModel, table=True):
    __tablename__ = "op_file_agent_link"
    __table_args__ = {"schema": SCHEMA_NAME} 

    op_id: UUID | None = Field(default=None, foreign_key="ops.op_files.op_id", primary_key=True)
    agent_id: UUID | None = Field(default=None, foreign_key="providers.international_agents.agent_id", primary_key=True)
