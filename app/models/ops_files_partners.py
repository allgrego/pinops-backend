
from sqlmodel import SQLModel, Field
from uuid import UUID

SCHEMA_NAME = 'ops'

"""
    Partners/Ops files link (many-to-many relationship)
"""

class OpsFilePartnerLink(SQLModel, table=True):
    __tablename__ = "op_file_partner_link"
    __table_args__ = {"schema": SCHEMA_NAME} 

    op_id: UUID | None = Field(default=None, foreign_key="ops.op_files.op_id", primary_key=True, ondelete='CASCADE')
    partner_id: UUID | None = Field(default=None, foreign_key="partners.partners.partner_id", primary_key=True, ondelete='CASCADE')
