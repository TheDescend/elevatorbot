from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.core.security.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash
from Backend.database.models import BackendUser
from Backend.schemas.auth import BackendUserModel, Token
from Backend.dependencies import get_db_session
from Backend import crud


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# generate and return a token
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)):
    user = await crud.backend_user.authenticate(
        db=db,
        user_name=form_data.username,
        password=form_data.password
    )

    # check if OK
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.user_name},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


# register a new user
@router.post("/register")
async def register(user_name: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db_session)):
    # look if a user with that name exists
    user = await crud.backend_user._get_with_key(db, user_name)
    if user:
        raise HTTPException(
            status_code=400,
            detail="An account with this user name already exists",
        )

    hashed_password = get_password_hash(password)

    # todo dont make everyone admin
    # _insert to db
    new_user = BackendUser(
        user_name=user_name,
        hashed_password=hashed_password,
        allowed_scopes=[],
        has_write_permission=True,
        has_read_permission=True,
    )
    await crud.backend_user._insert(db, new_user)

    # todo remove. just demonstration
    if new_user.user_name == "a":
        raise CustomException("wrongPw")

    return BackendUserModel.from_orm(new_user)

