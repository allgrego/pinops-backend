import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]