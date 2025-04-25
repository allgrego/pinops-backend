from sqlmodel import SQLModel, Field, Relationship
from app.models.clients import Client, ClientPublic
from app.models.carriers import Carrier, CarrierPublic
from app.models.partners import Partner, PartnerPublic
from app.models.users import User, UserPublic
from app.models.ops_files_partners import OpsFilePartnerLink
from app.models.geodata import Country, CountryPublic
from uuid import UUID, uuid4
from typing import Optional, List, Literal
from datetime import datetime, date

SCHEMA_NAME = "ops"

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
    op_type: Optional[str] = Field(default=None, max_length=100) # "maritime", "air", "road", "train", "other"
    # Locations
    origin_location: Optional[str] = Field(default=None, max_length=100) # City or port/airport
    # origin country is FK
    destination_location: Optional[str] = Field(default=None, max_length=100) # City or port/airport
    # destination country is FK
    # Schedules
    estimated_time_departure: Optional[date] = Field(default=None) # ETD
    actual_time_departure: Optional[date] = Field(default=None) #ATD
    estimated_time_arrival: Optional[date] = Field(default=None) # ETA
    actual_time_arrival: Optional[date] = Field(default=None) #ATA
    # Cargo properties
    cargo_description: Optional[str] = Field(default=None,  sa_column_kwargs={"name": "cargo_description"})
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

    # Foreign keys
    client_id: UUID = Field(foreign_key="clients.clients.client_id")
    status_id: int = Field(foreign_key="ops.op_status.status_id")
    carrier_id: Optional[UUID] = Field(foreign_key="carriers.carriers.carrier_id", default=None, sa_column_kwargs={"name": "carrier_id"}, ondelete='SET NULL')
    creator_user_id: Optional[UUID] = Field(foreign_key="users.users.user_id", default=None, sa_column_kwargs={"name": "creator_user_id"}, ondelete='SET NULL')
    assignee_user_id: Optional[UUID] = Field(foreign_key="users.users.user_id", default=None, sa_column_kwargs={"name": "asignee_user_id"}, ondelete='SET NULL')
    origin_country_id: Optional[int] = Field(foreign_key="geodata.countries.country_id", default=None, sa_column_kwargs={"name": "origin_country_id"}, ondelete='SET NULL')
    destination_country_id: Optional[int] = Field(foreign_key="geodata.countries.country_id", default=None, sa_column_kwargs={"name": "destination_country_id"}, ondelete='SET NULL')

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    # Relationships
    client: Client = Relationship(back_populates="ops_files")
    status: OpsStatus = Relationship(back_populates="ops_files") 
    carrier: Optional[Carrier] = Relationship(back_populates="ops_files") 
    partners: Optional[List[Partner]] = Relationship(back_populates="ops_files", link_model=OpsFilePartnerLink) 
    comments: List["OpsFileComment"] = Relationship(back_populates="ops_file", cascade_delete=True)   
    packaging: List["OpsFileCargoPackage"] = Relationship(back_populates="ops_file", cascade_delete=True)
    creator: Optional[User] = Relationship(back_populates="created_ops_files",  sa_relationship_kwargs={"foreign_keys": "[OpsFile.creator_user_id]"})
    assignee: Optional[User] = Relationship(back_populates="assigned_ops_files", sa_relationship_kwargs={"foreign_keys": "[OpsFile.assignee_user_id]"})
    origin_country: Optional[Country] = Relationship(back_populates="ops_files_origins", sa_relationship_kwargs={"foreign_keys": "[OpsFile.origin_country_id]"})
    destination_country: Optional[Country] = Relationship(back_populates="ops_files_destinations", sa_relationship_kwargs={"foreign_keys": "[OpsFile.destination_country_id]"})

class OpsFilePublic(OpsFileBase):
    op_id: UUID

    client: ClientPublic
    status: OpsStatusPublic
    
    carrier: Optional[CarrierPublic] = None
    partners: Optional[List[PartnerPublic]] = []
    
    comments: Optional[List["OpsFileCommentPublic"]] = []

    creator: Optional[UserPublic] = None
    assignee: Optional[UserPublic] = None

    origin_country: Optional[CountryPublic] = None
    destination_country: Optional[CountryPublic] = None

    packaging: Optional[List["OpsFileCargoPackagePublic"]] = []

    # Others
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class OpsFileCreate(OpsFileBase):
    client_id: UUID
    status_id: int
    op_type: Optional[Literal["maritime", "air", "road", "train", "other"]] = None
    origin_country_id: Optional[int] = None
    destination_country_id: Optional[int] = None
    # Partners and carrier
    carrier_id: Optional[UUID] = None
    partners_id: Optional[List[UUID]] = []
    # Cargo properties
    cargo_description: Optional[str] = None
    # Users properties
    creator_user_id: Optional[UUID] = None
    assignee_user_id: Optional[UUID] = None
    # Other properties
    comment: Optional["OpsFileCommentBase"] =  None # Only one comment could be added when creating
    packaging_data: Optional[List["OpsFileCargoPackageCreateWithoutOpId"]] = []

class OpsFileUpdate(OpsFileBase):
    client_id: Optional[UUID] = None
    status_id: Optional[int] = None
    op_type: Optional[Literal["maritime", "air", "road", "train", "other"]] = None

    origin_country_id: Optional[int] = None
    destination_country_id: Optional[int] = None
    carrier_id: Optional[UUID | None] = None
    partners_id: Optional[List[UUID]] = []
    # Cargo properties
    cargo_description: Optional[str] = None
    # Users properties
    creator_user_id: Optional[UUID] = None
    assignee_user_id: Optional[UUID] = None
    # Other properties
    packaging_data: Optional[List["OpsFileCargoPackageCreateWithoutOpId"]] = None

"""
    Ops file cargo packages
"""

class OpsFileCargoPackageBase(SQLModel):
    quantity: Optional[float] = None
    units: str = Field(default=None, max_length=20)   # e.g., "boxes", "units", "pallets", etc

class OpsFileCargoPackage(OpsFileCargoPackageBase, table=True):
    __tablename__ = "op_file_cargo_packages"
    __table_args__ = {"schema": SCHEMA_NAME}     

    package_id: int = Field(primary_key=True, sa_column_kwargs={"name": "package_id"})
    
    op_id: UUID = Field(foreign_key="ops.op_files.op_id")

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    # Relationships
    ops_file: OpsFile = Relationship(back_populates="packaging") 

class OpsFileCargoPackagePublic(OpsFileCargoPackageBase):
    package_id: int
    op_id: UUID

    # Others
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class OpsFileCargoPackageCreateWithoutOpId(OpsFileCargoPackageBase):
    quantity: Optional[float] = None
    units: str = Field(max_length=20)   # e.g., "boxes", "units", "pallets", etc

class OpsFileCargoPackageCreate(OpsFileCargoPackageCreateWithoutOpId):
    op_id: UUID

class OpsFileCargoPackageUpdate(OpsFileCargoPackageBase):
    quantity: Optional[float] = None
    units: Optional[str] = None   # e.g., "boxes", "units", "pallets", etc



"""
    Ops file comments
"""

class OpsFileCommentBase(SQLModel):
    content: str

class OpsFileComment(OpsFileCommentBase, table=True):
    __tablename__ = "op_file_comments"
    __table_args__ = {"schema": SCHEMA_NAME}     

    comment_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "comment_id"})
    
    # Foreign keys
    op_id: UUID = Field(foreign_key="ops.op_files.op_id")
    author_user_id: UUID = Field(foreign_key="users.users.user_id")

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    # Relationships
    ops_file: OpsFile = Relationship(back_populates="comments") 
    author: User = Relationship(back_populates="ops_files_comments") 

class OpsFileCommentPublic(OpsFileCommentBase):
    comment_id: UUID
    op_id: UUID
    author: Optional[UserPublic] = None

    # Others
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class OpsFileCommentCreateWithoutOpId(OpsFileCommentBase):
    author_user_id: Optional[UUID] = None
    content: str
class OpsFileCommentCreate(OpsFileCommentCreateWithoutOpId):
    op_id: UUID

class OpsFileCommentUpdate(OpsFileCommentBase):
    author_user_id: Optional[UUID] = None
    content: Optional[str] = None
