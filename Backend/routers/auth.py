from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from Backend.database.dataAccessLayers.backendUser import BackendUserDAL
from Backend.dependencies.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_password_hash
from Backend.schemas.auth import Token
from Backend.dependencies.databaseObjects import get_backend_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# generate and return a token
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), user_dal: BackendUserDAL = Depends(get_backend_user)):
    user = await user_dal.get_user(form_data.username)
    if await authenticate_user(user, form_data.password):
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
async def register(user_name: str = Form(...), password: str = Form(...), user_dal: BackendUserDAL = Depends(get_backend_user)):
    # look if a user with that name exists
    if await user_dal.get_user(user_name):
        raise HTTPException(
            status_code=400,
            detail="An account with this user name already exists",
        )
    hashed_password = get_password_hash(password)

    # todo dont make everyone admin
    # insert to db
    await user_dal.create_user(
        user_name=user_name,
        hashed_password=hashed_password,
        allowed_scopes=[],
        has_write_permission=True,
        has_read_permission=True,
    )
