from datetime import datetime
from typing import Literal, Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from app.models.geodata import Country

SCHEMA_NAME = 'carriers'


"""
    Carrier types
"""

class CarrierTypeBase(SQLModel):
    name: str = Field(max_length=50, unique=True)
    description: Optional[str] = Field(default=None, max_length=255)

class CarrierType(CarrierTypeBase, table=True):
    __tablename__ = "carrier_types"
    __table_args__ = {"schema": SCHEMA_NAME}

    carrier_type_id: str = Field(primary_key=True, max_length=50)

    # Relationships
    carriers: List["Carrier"] = Relationship(back_populates="carrier_type")

class CarrierTypePublic(CarrierTypeBase):
    carrier_type_id: str

class CarrierTypeCreate(CarrierTypeBase):
    pass

class CarrierTypeUpdate(CarrierTypeBase):
    name: Optional[str] = None
    description: Optional[str] = None

"""
    Carriers
"""

class CarrierBase(SQLModel):
    name: str = Field(max_length=255, nullable=False, unique=True)
    tax_id: Optional[str] = Field(default=None, max_length=100, unique=True)
    disabled: Optional[bool] = Field(default=False)

class Carrier(CarrierBase, table=True):
    __tablename__ = "carriers"
    __table_args__ = {"schema": SCHEMA_NAME}

    carrier_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "carrier_id"})

    # Foreign keys
    carrier_type_id: str = Field(foreign_key=f"{SCHEMA_NAME}.carrier_types.carrier_type_id", nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    carrier_type: CarrierType = Relationship(back_populates="carriers")
    carrier_contacts: List["CarrierContact"] = Relationship(back_populates="carrier")
    ops_files: Optional[List["OpsFile"]] = Relationship(back_populates="carrier") 

class CarrierPublic(CarrierBase):
    carrier_id: UUID

    created_at: datetime 
    updated_at: datetime 

    carrier_type: CarrierType

class CarrierCreate(CarrierBase):
    carrier_type_id: str

class CarrierUpdate(CarrierBase):
    name: Optional[str] = None
    carrier_type_id: Optional[str] = None


"""
    Carriers contact
"""

class CarrierContactBase(SQLModel):
    name: str = Field(max_length=255, nullable=False, unique=True)
    position: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    mobile: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=100)   
    disabled: Optional[bool] = Field(default=False)


class CarrierContact(CarrierContactBase, table=True):
    __tablename__ = "carrier_contacts"
    __table_args__ = {"schema": SCHEMA_NAME}

    carrier_contact_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "carrier_contact_id"})

    # Foreign keys
    carrier_id: UUID = Field(foreign_key=f"{SCHEMA_NAME}.carriers.carrier_id", nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    carrier: Carrier = Relationship(back_populates="carrier_contacts")

class CarrierContactPublic(CarrierContactBase):
    carrier_contact_id: UUID
    carrier_id: UUID
    created_at: datetime 
    updated_at: datetime

class CarrierContactCreate(CarrierContactBase):
    carrier_id: str
    name: str
    position: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    disabled: Optional[bool] = False

class CarrierContactUpdate(CarrierContactBase):
    carrier_id: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    disabled: Optional[bool] = False
