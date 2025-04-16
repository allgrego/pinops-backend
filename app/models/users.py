from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List, Optional


SCHEMA_NAME = "users"

"""
    Users roles
"""

class UserRoleBase(SQLModel):
    role_name: str = Field(max_length=255, unique=True)

class UserRole(UserRoleBase, table=True):
    __tablename__ = "roles"
    __table_args__ = {"schema": SCHEMA_NAME}

    role_id: str = Field(primary_key=True, max_length=50, sa_column_kwargs={"name": "role_id"})

    # Relationships
    users: List["User"] = Relationship(back_populates="role")

class UserRolePublic(UserRoleBase):
    role_id: str

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleUpdate(UserRoleBase):
    role_name: Optional[str] = None

"""
    Users
"""

class UserBase(SQLModel):
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True, index=True)
    disabled: bool = Field(default=False)

class User(UserBase, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": SCHEMA_NAME}

    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    role_id: Optional[str] = Field(foreign_key=f"{SCHEMA_NAME}.roles.role_id", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    hashed_password: str
    
    # Relationship
    role: Optional[UserRole] = Relationship(back_populates="users")
    created_ops_files: Optional[List["OpsFile"]] = Relationship(back_populates="creator", sa_relationship_kwargs={"foreign_keys": "[OpsFile.creator_user_id]"})
    assigned_ops_files: Optional[List["OpsFile"]] = Relationship(back_populates="assignee", sa_relationship_kwargs={"foreign_keys": "[OpsFile.assignee_user_id]"})
    ops_files_comments: Optional[List["OpsFileComment"]] = Relationship(back_populates="author") 



class UserPublic(UserBase):
    user_id: UUID
    role: Optional[UserRolePublic] = None

class UserCreate(UserBase):
    password: str
    role_id: str

class UserUpdate(UserBase):
    name: Optional[str] = None
    disabled: Optional[bool] = None
    password: Optional[str] = None
    role_id: Optional[str] = None

class UserLogin(SQLModel):
    email: str
    password: str
