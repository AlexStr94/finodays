from datetime import date
from typing import Generic, List, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import extract, select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.db import Base
from exceptions.base import CardNotFoundException
from models import base as models
from schemas import base as schemas


class Repository:
    def all(self, *args, **kwargs):
        raise NotImplementedError

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_or_create(self, *args, **kwargs):
        raise NotImplementedError
    
    def filter_by(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError
    

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def create(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType
        ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def all(self, db: AsyncSession) -> List[ModelType]:
        statement = select(self._model)
        results = await db.execute(statement=statement)
        lst = results.scalars().all()
        return lst
    
    async def filter_by(self, db: AsyncSession, **kwargs) -> List[ModelType]:
        statement = select(self._model).filter_by(**kwargs)
        results = await db.execute(statement=statement)
        lst = results.scalars().all()
        return lst
    
    async def get(self, db: AsyncSession, **kwargs) -> ModelType | None:
        results: List[ModelType] = await self.filter_by(db, **kwargs)
        if len(results) > 1:
            raise MultipleResultsFound
        if results:
            return results[0]
        return None
        

class RepositoryUser(RepositoryDB[models.User, schemas.UserCreate]):
    async def create(
            self,
            db: AsyncSession,
            obj_in: schemas.UserCreate
        ) -> models.User:
        birth_date = obj_in.birth_date
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data['birth_date'] = birth_date
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    

class RepositoryBank(RepositoryDB[models.Bank, schemas.BankCreate]):
    pass


class RepositoryCard(RepositoryDB[models.Card, schemas.CardCreate]):
    async def filter_by(self, db: AsyncSession, **kwargs) -> List[models.Card]:
        statement = select(self._model) \
            .filter_by(**kwargs) \
            .options(selectinload(self._model.bank))
        results = await db.execute(statement=statement)
        lst = results.scalars().all()
        return lst


class RepositoryCashback(
    RepositoryDB[models.Cashback, schemas.CashbackCreate]
):
    pass


class RepositoryUserCashback(
    RepositoryDB[models.UserCashback, schemas.UserCashbackCreate]
):
    async def create(
            self,
            db: AsyncSession,
            obj_in: schemas.UserCashbackCreate
        ) -> models.UserCashback:
        month = obj_in.month
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data['month'] = month
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def card_cashbacks(
        self,
        db: AsyncSession,
        card_number: str,
        month: date
    ):
        card: models.Card | None = await card_crud.get(
            db=db, card_number=card_number
        )

        if not card:
            raise CardNotFoundException
        
        statement = select(self._model) \
            .where(
                self._model.card == card,
                self._model.month == month
            ) \
            .options(selectinload(self._model.cashback))
        
        results = await db.execute(statement=statement)
        return results.scalars().all()
    

class RepositoryTransaction(
    RepositoryDB[models.Transaction, schemas.TransactionCreate]
):
    async def create(
            self, db: AsyncSession,
            obj_in: schemas.TransactionCreate
        ) -> models.Transaction:
        time = obj_in.time
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data['time'] = time
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_card_transactions(
        self,
        db: AsyncSession,
        card_number: str,
        month: date
    ) -> List[models.Transaction]:
        card: models.Card | None = await card_crud.get(
            db=db, card_number=card_number
        )

        if not card:
            raise CardNotFoundException
        
        statement = select(self._model) \
            .where(self._model.card == card) \
            .filter(
                extract('month', self._model.time) == month.month,
                extract('year', self._model.time) == month.year,
            ) \
            .order_by(self._model.time)
            
        results = await db.execute(statement=statement)
        return results.scalars().all()


user_crud = RepositoryUser(models.User)
bank_crud = RepositoryBank(models.Bank)
card_crud = RepositoryCard(models.Card)
cashback_crud = RepositoryCashback(models.Cashback)
user_cashback_crud = RepositoryUserCashback(models.UserCashback)
transaction_crud = RepositoryTransaction(models.Transaction)
