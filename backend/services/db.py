from typing import Generic, Type, TypeVar
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


from pydantic import BaseModel

from db.db import Base
from exceptions import db as exceptions
from models import base as models
from schemas import base as schemas


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_or_create(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError
    

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    

class RepositoryUser(RepositoryDB[models.User, schemas.GosuslugiUser, schemas.GosuslugiUser]):
    async def create(self, db: AsyncSession, obj_in: schemas.User) -> ModelType:
        obj_in_data: dict = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as e:
            raise exceptions.UserAlreadyExist
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, gosuslugi_id: str) -> ModelType:
        statement = select(self._model).where(self._model.gosuslugi_id == gosuslugi_id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()
    
    async def get_or_create(self, db: AsyncSession, obj_in: schemas.User) -> ModelType:
        obj_in_data: dict = jsonable_encoder(obj_in)
        user: models.User | None = await self.get(db, obj_in_data.get('gosuslugi_id'))
        if not user:
            user = await self.create(db, obj_in)
        
        return user
    

user_crud = RepositoryUser(models.User)