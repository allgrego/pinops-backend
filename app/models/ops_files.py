from sqlmodel import SQLModel, Field, Relationship
from app.models.clients import Client, ClientPublic
from app.models.carriers import Carrier, CarrierPublic
from app.models.international_agents import InternationalAgent, InternationalAgentPublic
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, date

SCHEMA_NAME = 'ops'

"""
    File statuses
"""

class OpsStatusBase(SQLModel):
    status_name: str = Field(max_length=50, unique=True)

class OpsStatus(OpsStatusBase, table=True):
    __tablename__ = "op_status"
    __table_args__ = {"schema": SCHEMA_NAME}

    status_id: int = Field(primary_key=True)

    ops_files: List["OpsFile"] = Relationship(back_populates="status")

class OpsStatusPublic(OpsStatusBase):
    status_id: int

class OpsStatusCreate(OpsStatusBase):
    status_name: str

class OpsStatusUpdate(OpsStatusBase):
    status_name: str

"""
    Ops files
"""

class OpsFileBase(SQLModel):
    # Locations
    origin_location: Optional[str] = Field(default=None, max_length=100) # City or port/airport
    origin_country: Optional[str] = Field(default=None, max_length=100) # country code
    destination_location: Optional[str] = Field(default=None, max_length=100) # City or port/airport
    destination_country: Optional[str] = Field(default=None, max_length=100) # country code
    # Schedules
    estimated_time_departure: Optional[date] = Field(default=None) # ETD
    actual_time_departure: Optional[date] = Field(default=None) #ATD
    estimated_time_arrival: Optional[date] = Field(default=None) # ETA
    actual_time_arrival: Optional[date] = Field(default=None) #ATA
    # Cargo properties
    cargo_description: Optional[str] = Field(default=None,  sa_column_kwargs={"name": "cargo_description"})
    units_quantity: Optional[float] = Field(default=None)  # The number of units
    units_type: Optional[str] = Field(default=None, max_length=50)   # e.g., "boxes", "pallets", "units"
    gross_weight_value: Optional[float] = Field(default=None)  # The value of gross weight
    gross_weight_unit: Optional[str] = Field(default=None, max_length=20)   # e.g., "kg", "lbs"
    volume_value: Optional[float] = Field(default=None)       # The value of volume
    volume_unit: Optional[str] = Field(default=None, max_length=20)    # e.g., "m3", "L", "ft3"
    # Op details
    master_transport_doc: Optional[str] = Field(default=None, max_length=100) # MBL/MAWB
    house_transport_doc: Optional[str] = Field(default=None, max_length=100) # HBL/HAWB
    incoterm: Optional[str] = Field(default=None, max_length=16)
    modality: Optional[str] = Field(default=None, max_length=100)
    voyage: Optional[str] = Field(default=None, max_length=100) # Voyage and ship info

    
    
class OpsFile(OpsFileBase, table=True):
    __tablename__ = "op_files"
    __table_args__ = {"schema": SCHEMA_NAME} 

    op_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "op_id"})
    client_id: UUID = Field(foreign_key="clients.clients.client_id")
    status_id: int = Field(foreign_key="ops.op_status.status_id")
    
    # Providers
    agent_id: Optional[UUID] = Field(default=None, foreign_key="providers.international_agents.agent_id", sa_column_kwargs={"name": "international_agent_id"})
    carrier_id: Optional[UUID] = Field(default=None, foreign_key="providers.carriers.carrier_id", sa_column_kwargs={"name": "carrier_id"})

    # Relationships
    client: Client = Relationship(back_populates="ops_files")
    status: OpsStatus = Relationship(back_populates="ops_files") 
    carrier: Optional[Carrier] = Relationship(back_populates="ops_files") 
    agent: Optional[InternationalAgent] = Relationship(back_populates="ops_files") 
    

class OpsFilePublic(OpsFileBase):
    op_id: UUID

    client: ClientPublic
    status: OpsStatusPublic
    
    # Providers
    carrier: Optional[CarrierPublic] = None
    agent: Optional[InternationalAgentPublic] = None

    # Others
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class OpsFileCreate(OpsFileBase):
    client_id: UUID

    status_id: int
    # Providers
    carrier_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    # Cargo properties
    cargo_description: Optional[str] = None

class OpsFileUpdate(OpsFileBase):
    client_id: Optional[UUID] = None
    status_id: Optional[int] = None
    # Providers
    carrier_id: Optional[UUID | None] = None
    agent_id: Optional[UUID] | None = None
    # Cargo properties
    cargo_description: Optional[str] = None