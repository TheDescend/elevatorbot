from fastapi import Depends, FastAPI

from Backend.database.base import setup_engine
from Backend.database.models import BackendUser, create_tables
from Backend.dependencies import auth_get_user_with_read_perm, auth_get_user_with_write_perm
from Backend.endpoints import auth, items
from Backend.schemas.auth import BackendUserModel


app = FastAPI()

app.include_router(items.router)
app.include_router(auth.router)


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
    # insert db tables
    await create_tables(engine=setup_engine())
