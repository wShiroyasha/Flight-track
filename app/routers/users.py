from .. import schemas, utils, models
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database import  get_db

router = APIRouter()

@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(email=str(user.email).lower(), password=hashed_password)

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )
    db.refresh(new_user)

    return new_user