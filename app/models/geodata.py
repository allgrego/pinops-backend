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


class CountryPublic(CountryBase):
    country_id: int 


class CountryCreate(CountryBase):
    pass

class CountryUpdate(CountryBase):
    name: Optional[str] = None
    iso2_code: Optional[str] = None
    iso3_code: Optional[str] = None
