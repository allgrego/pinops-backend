from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List, Optional

class ClientBase(SQLModel):
    name: str = Field(default=None, unique=True, max_length=255)
    tax_id: Optional[str] = Field(default=None, max_length=100, unique=True)
    address: Optional[str] = Field(default=None)
    contact_name: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=100)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    disabled: Optional[bool] = Field(default=False)


class Client(ClientBase, table=True):
    __tablename__ = "clients"
    __table_args__ = {"schema": "clients"}  # Replace with your schema name

    client_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "client_id"})

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    ops_files: List["OpsFile"] = Relationship(back_populates="client")


class ClientPublic(ClientBase):
    client_id: UUID 

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    name: Optional[str] = None
