import os

from fastapi import Depends, FastAPI

from Backend.database.base import Base, engine
from Backend.database.models import create_tables
from Backend.dependencies import get_query_token, get_token_header
from Backend.internal import admin
from Backend.routers import items


app = FastAPI(dependencies=[Depends(get_query_token)])

app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}



@app.on_event("startup")
async def startup():
    DATABASE_URL = f"""postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}/{os.environ.get("POSTGRES_DB")}"""
    print(DATABASE_URL)

    # create db tables
    async with engine.begin() as connection:
        await create_tables(connection)


# https://towardsdatascience.com/build-an-async-python-service-with-fastapi-sqlalchemy-196d8792fa08
