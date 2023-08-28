from datetime import date
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
        user: models.User | None = await self.get(db, obj_in.gosuslugi_id)
        if not user:
            user = await self.create(db, obj_in)
        
        return user
    

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
    

class RepositoryCard(RepositoryDB[models.Card, schemas.Card, schemas.Card]):
    async def create(self, db: AsyncSession, obj_in: schemas.Card) -> ModelType:
        obj_in_data: dict = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as e:
            raise exceptions.CardAlreadyExist
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, card_number: str) -> ModelType:
        statement = select(self._model).where(self._model.card_number == card_number)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()
    
    async def get_or_create(self, db: AsyncSession, obj_in: schemas.Card) -> ModelType:
        card: models.Card | None = await self.get(db, obj_in.card_number)
        if not card:
            card = await self.create(db, obj_in)
        
        return card
    

class RepositoryCashback(RepositoryDB[models.Cashback, schemas.Cashback, schemas.Cashback]):
    async def create(self, db: AsyncSession, obj_in: schemas.Cashback) -> ModelType:
        obj_in_data: dict = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as e:
            raise exceptions.CashbackAlreadyExist
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, product_type: str, value: int) -> ModelType:
        statement = select(self._model) \
            .where(
                self._model.product_type == product_type,
                self._model.value == value,
            )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()
    
    async def get_or_create(self, db: AsyncSession, obj_in: schemas.Cashback) -> ModelType:
        cashback: models.Cashback | None = await self.get(
            db,
            product_type=obj_in.product_type,
            value=obj_in.value
        )
        if not cashback:
            cashback = await self.create(db, obj_in)
        
        return cashback
    

class RepositoryUserCashback(RepositoryDB[models.UserCashback, schemas.UserCashback, schemas.UserCashback]):
    async def create(self, db: AsyncSession, obj_in: schemas.UserCashback) -> ModelType:
        db_obj = self._model(
            card_id=obj_in.card_id,
            cashback_id=obj_in.cashback_id,
            month=obj_in.month,
            status=obj_in.status
        )
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as e:
            raise exceptions.UserCashbackAlreadyExist
        await db.refresh(db_obj)
        return db_obj
    
    async def get(
            self,
            db: AsyncSession,
            obj_in: schemas.UserCashback
        ) -> ModelType:
        statement = select(self._model) \
            .where(
                self._model.card_id == obj_in.card_id,
                self._model.cashback_id == obj_in.cashback_id,
                self._model.month == obj_in.month,
                self._model.status == obj_in.status
            )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()
    
    async def get_or_create(self, db: AsyncSession, obj_in: schemas.UserCashback) -> ModelType:
        user_cashback: models.UserCashback | None = await self.get(
            db=db,
            obj_in=obj_in
        )
        if not user_cashback:
            user_cashback = await self.create(db, obj_in)
        
        return user_cashback


user_crud = RepositoryUser(models.User)
card_crud = RepositoryCard(models.Card)
cashback_crud = RepositoryCashback(models.Cashback)
user_cashback_crud = RepositoryUserCashback(models.UserCashback)