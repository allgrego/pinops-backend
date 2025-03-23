from datetime import datetime
from typing import Literal, Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4

SCHEMA_NAME = 'providers'

"""
    Carriers
"""

class CarrierBase(SQLModel):
    name: str = Field(default=None)
    type: str = Field()
    contact_name: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=100)
    contact_email: Optional[str] = Field(default=None, max_length=255)

class Carrier(CarrierBase, table=True):
    __tablename__ = "carriers"
    __table_args__ = {"schema": SCHEMA_NAME}

    carrier_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "carrier_id"})

    ops_files: Optional[List["OpsFile"]] = Relationship(back_populates="carrier")

class CarrierPublic(CarrierBase):
    carrier_id: UUID

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class CarrierCreate(CarrierBase):
    type: Literal["shipping_line", "airline"]

class CarrierUpdate(CarrierBase):
    name: Optional[str] = None
    type: Optional[Literal["shipping_line", "airline"]] = None

