from datetime import date, datetime
from typing import Generic, List, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.db import Base
from exceptions.base import AccountNotFoundException
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
        obj_in_data = obj_in.dict()
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
    pass
    

class RepositoryBank(RepositoryDB[models.Bank, schemas.BankCreate]):
    pass


class RepositoryAccount(RepositoryDB[models.Account, schemas.AccountCreate]):
    async def filter_by(
            self,
            db: AsyncSession,
            with_bank: bool = False,
            with_cards: bool = False,
            with_cashbacks: bool = False,
            with_transactions: bool = False,
            **kwargs
        ) -> List[models.Account]:
        statement = select(self._model).filter_by(**kwargs)
        if with_cards:
            statement = statement \
                .options(selectinload(self._model.cards))
        if with_bank:
            statement = statement \
                .options(selectinload(self._model.bank))
        if with_cashbacks:
            statement = statement \
                .options(selectinload(self._model.cashbacks))
        if with_transactions:
            statement = statement \
                .options(selectinload(self._model.transactions))
        results = await db.execute(statement=statement)
        lst = results.scalars().all()
        return lst


class RepositoryCard(RepositoryDB[models.Card, schemas.CardCreate]):
    async def filter_by(self, db: AsyncSession, **kwargs) -> List[models.Card]:
        statement = select(self._model) \
            .filter_by(**kwargs)
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
    async def account_cashbacks(
        self,
        db: AsyncSession,
        account_number: str,
        month: date
    ):
        account: models.Account | None = await account_crud.get(
            db=db, number=account_number
        )

        if not account:
            raise AccountNotFoundException
        
        statement = select(self._model) \
            .where(
                self._model.account == account,
                self._model.month == month
            ) \
            .options(selectinload(self._model.cashback))
        
        results = await db.execute(statement=statement)
        return results.scalars().all()
    

class RepositoryTransaction(
    RepositoryDB[models.Transaction, schemas.TransactionCreate]
):    
    async def get_account_transactions(
        self,
        db: AsyncSession,
        account_number: str,
        start_datetime: datetime | None
    ) -> List[models.Transaction]:
        account: models.Card | None = await account_crud.get(
            db=db, number=account_number
        )

        if not account:
            raise AccountNotFoundException
        
        statement = select(self._model) \
            .filter(self._model.account == account) 
        
        if start_datetime:
            statement = statement.filter(self._model.time > start_datetime)
            
        statement = statement.order_by(self._model.time)
            
        results = await db.execute(statement=statement)
        return results.scalars().all()


user_crud = RepositoryUser(models.User)
bank_crud = RepositoryBank(models.Bank)
account_crud = RepositoryAccount(models.Account)
card_crud = RepositoryCard(models.Card)
cashback_crud = RepositoryCashback(models.Cashback)
user_cashback_crud = RepositoryUserCashback(models.UserCashback)
transaction_crud = RepositoryTransaction(models.Transaction)
