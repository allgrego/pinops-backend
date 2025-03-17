from typing import Literal, Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4

SCHEMA_NAME = 'providers'

"""
    Carriers
"""

class CarrierBase(SQLModel):
    name: str = Field(default=None)
    type: str

class Carrier(CarrierBase, table=True):
    __tablename__ = "carriers"
    __table_args__ = {"schema": SCHEMA_NAME}

    carrier_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "carrier_id"})

    ops_files: Optional[List["OpsFile"]] = Relationship(back_populates="carrier")

class CarrierPublic(CarrierBase):
    carrier_id: UUID

class CarrierCreate(CarrierBase):
    name: str
    type: Literal["shipping_line", "airline"]

class CarrierUpdate(CarrierBase):
    name: Optional[str] = None
    type: Optional[Literal["shipping_line", "airline"]] = None

