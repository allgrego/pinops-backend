from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List, Optional

class CountryBase(SQLModel):
    name: str = Field(nullable=False, unique=True, max_length=255)
    iso2_code: str = Field(nullable=False, unique=True, max_length=2)
    iso3_code: str = Field(nullable=False, unique=True, max_length=3)


class Country(CountryBase, table=True):
    __tablename__ = "countries"
    __table_args__ = {"schema": "geodata"} 

    country_id: int = Field(primary_key=True)
     
    # Relationships
    partners: List["Partner"] = Relationship(back_populates="country")
    ops_files_origins: Optional[List["OpsFile"]] = Relationship(back_populates="origin_country", sa_relationship_kwargs={"foreign_keys": "[OpsFile.origin_country_id]"})
    ops_files_destinations: Optional[List["OpsFile"]] = Relationship(back_populates="destination_country", sa_relationship_kwargs={"foreign_keys": "[OpsFile.destination_country_id]"})

class CountryPublic(CountryBase):
    country_id: int 


class CountryCreate(CountryBase):
    pass

class CountryUpdate(CountryBase):
    name: Optional[str] = None
    iso2_code: Optional[str] = None
    iso3_code: Optional[str] = None
