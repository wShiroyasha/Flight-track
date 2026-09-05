from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import database, schemas, models, utils, oauth2

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    email = user_credentials.username.strip().lower()
    user = db.scalar(
        select(models.User).where(models.User.email == email)
    )

    password_hash = user.password if user is not None else utils.dummy_password_hash
    password_valid = utils.verify_password(user_credentials.password, password_hash)
    if user is None or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}