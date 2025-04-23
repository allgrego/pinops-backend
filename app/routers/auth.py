from fastapi import APIRouter,  HTTPException
from sqlmodel import select, func
from app.database import SessionDep
from app.models.users import User, UserPublic, UserLogin
from app.lib.crypto import verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=UserPublic)
def login(user: UserLogin, db: SessionDep):
    email = user.email.lower().strip()

    db_user = db.exec(select(User).where(func.lower(User.email) == email)).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    is_valid_password = verify_password(user.password, db_user.hashed_password)
    
    if not is_valid_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return db_user
