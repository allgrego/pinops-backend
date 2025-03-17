from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List

class ClientBase(SQLModel):
    name: str = Field(default=None)


class Client(ClientBase, table=True):
    __tablename__ = "clients"
    __table_args__ = {"schema": "clients"}  # Replace with your schema name

    client_id: UUID = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"name": "client_id"})

    ops_files: List["OpsFile"] = Relationship(back_populates="client")

class ClientPublic(ClientBase):
    client_id: UUID 

class ClientCreate(ClientBase):
    name: str

class ClientUpdate(ClientBase):
    name: str