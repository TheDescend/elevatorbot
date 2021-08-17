from fastapi import Depends, FastAPI

from Backend.database.base import setup_engine
from Backend.database.models import BackendUser, create_tables
from Backend.dependencies.auth import auth_get_user_with_read_perm, auth_get_user_with_write_perm
from Backend.routers import items, auth
from Backend.schemas.auth import BackendUserModel


app = FastAPI()

app.include_router(items.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


# only allow people with read permissions
@app.get("/read_perm", response_model=BackendUserModel)
async def read_perm(user: BackendUser = Depends(auth_get_user_with_read_perm)):
    return BackendUserModel.from_orm(user)


# only allow people with write permissions
@app.get("/write_perm", response_model=BackendUserModel)
async def write_perm(user: BackendUser = Depends(auth_get_user_with_write_perm)):
    return BackendUserModel.from_orm(user)


@app.on_event("startup")
async def startup():
    # create db tables
    async with setup_engine().begin() as connection:
        await create_tables(connection)


# https://towardsdatascience.com/build-an-async-python-service-with-fastapi-sqlalchemy-196d8792fa08
