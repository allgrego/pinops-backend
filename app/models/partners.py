from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from app.models.geodata import Country, CountryPublic
from app.models.ops_files_partners import OpsFilePartnerLink

SCHEMA_NAME = 'partners'


"""
    Partner types
"""

class PartnerTypeBase(SQLModel):
    name: str = Field(max_length=50, unique=True)
    description: Optional[str] = Field(default=None, max_length=255)

class PartnerType(PartnerTypeBase, table=True):
    __tablename__ = "partner_types"
    __table_args__ = {"schema": SCHEMA_NAME}

    partner_type_id: str = Field(primary_key=True, max_length=50)

    # Relationships
    partners: List["Partner"] = Relationship(back_populates="partner_type")

class PartnerTypePublic(PartnerTypeBase):
    partner_type_id: str

class PartnerTypeCreate(PartnerTypeBase):
    pass

class PartnerTypeUpdate(PartnerTypeBase):
    name: Optional[str] = None
    description: Optional[str] = None

"""
    Partners
"""

class PartnerBase(SQLModel):
    name: str = Field(max_length=255, nullable=False, unique=True)
    tax_id: Optional[str] = Field(default=None, max_length=100, unique=True)
    webpage: Optional[str] = Field(default=None, max_length=255)
    disabled: Optional[bool] = Field(default=False)


class Partner(PartnerBase, table=True):
    __tablename__ = "partners"
    __table_args__ = {"schema": SCHEMA_NAME}

    partner_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "partner_id"})

    # Foreign keys
    partner_type_id: str = Field(foreign_key=f"{SCHEMA_NAME}.partner_types.partner_type_id", nullable=False)
    country_id: Optional[int] = Field(foreign_key=f"geodata.countries.country_id", default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    partner_type: PartnerType = Relationship(back_populates="partners")
    partner_contacts: List["PartnerContact"] = Relationship(back_populates="partner")
    country: Optional[Country] = Relationship(back_populates="partners")
    ops_files: Optional[List["OpsFile"]] = Relationship(back_populates="partners", link_model=OpsFilePartnerLink) 

class PartnerPublic(PartnerBase):
    partner_id: UUID

    created_at: datetime 
    updated_at: datetime 

    partner_type: PartnerType
    country: Optional[CountryPublic] = None

    partner_contacts:Optional[List["PartnerContactPublic"]] = []

class PartnerCreate(PartnerBase):
    partner_type_id: str
    country_id: Optional[int] = None
    initial_contacts: Optional[List["PartnerContactCreateBase"]] = []

class PartnerUpdate(PartnerBase):
    name: Optional[str] = None
    partner_type_id: Optional[str] = None
    country_id: Optional[int] = None
    partner_contacts: Optional[List["PartnerContactCreateBase"]] = None


"""
    Partners contact
"""

class PartnerContactBase(SQLModel):
    name: str = Field(max_length=255, nullable=False, unique=True)
    position: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    mobile: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=100)   
    disabled: Optional[bool] = Field(default=False)


class PartnerContact(PartnerContactBase, table=True):
    __tablename__ = "partner_contacts"
    __table_args__ = {"schema": SCHEMA_NAME}

    partner_contact_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "partner_contact_id"})

    # Foreign keys
    partner_id: UUID = Field(foreign_key=f"{SCHEMA_NAME}.partners.partner_id", nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    partner: Partner = Relationship(back_populates="partner_contacts")

class PartnerContactPublic(PartnerContactBase):
    partner_contact_id: UUID
    partner_id: UUID
    created_at: datetime 
    updated_at: datetime

class PartnerContactCreateBase(PartnerContactBase):
    name: str
    position: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    disabled: Optional[bool] = False

class PartnerContactCreate(PartnerContactCreateBase):
    partner_id: str

class PartnerContactUpdate(PartnerContactBase):
    partner_id: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    disabled: Optional[bool] = False

