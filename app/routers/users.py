from fastapi import APIRouter,  HTTPException
from sqlmodel import select, desc
from app.database import SessionDep
from app.models.users import User, UserPublic, UserCreate, UserUpdate
from uuid import UUID
from app.lib.crypto import hash_password, generate_salt

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserPublic)
def create_user(user: UserCreate, db: SessionDep):

    salt = generate_salt()

    hashed_password = hash_password(user.password, salt)
    
    extra_data = {
        "hashed_password": hashed_password.strip(), 
        "email": str(user.email).lower().strip(),
        "name": str(user.name).strip()
    }
    
    db_user = User.model_validate(user, update=extra_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=list[UserPublic]) 
def read_users(db: SessionDep):
    Users = db.exec(select(User).order_by(desc(User.created_at))).all()
    return Users

@router.get("/{user_id}/", response_model=UserPublic)
def read_user(user_id: UUID, db: SessionDep):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User


@router.patch("/{user_id}/", response_model=UserPublic)
def update_user(user_id: UUID, User: UserUpdate, db: SessionDep):
    user_db = db.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = User.model_dump(exclude_unset=True)
    
    if "password" in user_data:
        hashed_password = hash_password(user_data["password"])
        user_data["hashed_password"] = hashed_password
        del user_data["password"]

    user_db.sqlmodel_update(user_data)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@router.delete("/{user_id}/")
def delete_user(user_id: UUID, db: SessionDep):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True} 