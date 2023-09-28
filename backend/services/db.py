from asyncpg.exceptions import UniqueViolationError
from datetime import date, datetime, timedelta, timezone
from dateutil import relativedelta
from typing import Generic, List, Type, TypeVar
from fastapi.encoders import jsonable_encoder
import orjson
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, MultipleResultsFound
from sqlalchemy.orm import selectinload, subqueryload


from pydantic import BaseModel

from db.db import Base
from exceptions import db as exceptions
from models import base as models
from schemas import base as schemas
from .cashback import can_choose_cashback


class Repository:

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
    
    def bulk_update(self, *args, **kwargs):
        raise NotImplementedError
    

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryDB(
    Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):
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
    
    async def bulk_create(
        self,
        db: AsyncSession,
        objs_in: List[CreateSchemaType]
    ) -> List[ModelType]:
        try:
            db_objs = [
                self._model(**obj.dict())
                for obj in objs_in
            ]
            db.add_all(db_objs)
            await db.commit()
            # await db.refresh(db_objs)
        except IntegrityError:
            await db.rollback()
    
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
    
    async def get_or_create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj: ModelType | None = await self.get(db, **obj_in.dict())
        if not obj:
            obj = await self.create(db, obj_in)
        
        return obj
    
    async def update(
        self,
        db: AsyncSession,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        obj_in_data = obj_in.dict()
        db_obj: ModelType | None = await self.get(
            db,
            id=obj_in_data.get('id')
        )
        if db_obj:
            for attribute, value in obj_in_data.items():
                if attribute != 'id' and value != None:
                    setattr(db_obj, attribute, value)
                
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        raise exceptions.UserCashbackDoesNotExist #exception type add
    

class RepositoryUser(RepositoryDB[models.User, schemas.User, schemas.User]):
    async def get(self, db: AsyncSession, gosuslugi_id: str) -> models.User:
        statement = select(self._model).where(self._model.gosuslugi_id == gosuslugi_id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()
    
    async def get_or_create(self, db: AsyncSession, obj_in: schemas.User) -> models.User:
        user: models.User | None = await self.get(db, gosuslugi_id=obj_in.gosuslugi_id)
        if not user:
            user = await self.create(db, obj_in)
        
        return user


class RepositoryAccount(RepositoryDB[models.Account, schemas.AccountCreate, schemas.AccountUpdate]):
    async def get_user_accounts(
        self,
        db: AsyncSession,
        user_id: int,
        month: date
    ) -> List[schemas.AccountWithCardsAndCashbacks]:
        statement = select(self._model, models.UserCashback) \
            .filter(self._model.user_id == user_id) \
            .filter(
                models.UserCashback.month == month,
                models.UserCashback.status == True,
            ) \
            .options(selectinload(self._model.cards)) \
            .options(selectinload(self._model.cashbacks)) \
            .options(selectinload(models.UserCashback.cashback))
        
        results = await db.execute(statement=statement)

        accounts = set()
        user_cashbacks = set()
        for account, user_cashback in results.all():
            accounts.add(account)
            user_cashbacks.add(user_cashback)

        result = []
        for account in accounts:
            cashbacks: List[models.UserCashback] = list(
                filter(lambda x: x.account_id == account.id, user_cashbacks)
            )
            account_info = schemas.AccountWithCardsAndCashbacks(
                account_number=account.number,
                bank=account.bank,
                can_choose_cashback=can_choose_cashback(account),
                cashbacks=[
                    schemas.Cashback(
                        product_type=cashback.cashback.product_type,
                        value=cashback.value
                    )
                    for cashback in cashbacks
                ],
                cards=[
                    schemas.Card(
                        last_four_digits=card.card_number[-4:]
                    )
                    for card in account.cards
                ]
            )

            result.append(account_info)

        return result
    

    async def get_user_accounts_with_transactions(
        self,
        db: AsyncSession,
        user_id: int,
        month: date
    ) -> List[schemas.AccountWithTransactions]:
        start_time = datetime(
            year=month.year,
            month=month.month,
            day=1,
            # tzinfo=timezone.utc
        )
        end_time = start_time + relativedelta.relativedelta(months=1)
        statement = select(self._model, models.Transaction) \
            .filter(self._model.user_id == user_id) \
            .filter(models.Transaction.time >= start_time) \
            .filter(models.Transaction.time < end_time)
        
        results = await db.execute(statement=statement)

        accounts = set()
        transactions = set()
        for account, transaction in results.all():
            accounts.add(account)
            transactions.add(transaction)

        result = []
        for account in accounts:
            account_transactions: List[models.Transaction] = list(
                filter(lambda x: x.account_id == account.id, transactions)
            )
            account_transactions = list(
                sorted(account_transactions, key=lambda x: x.time)
            )
            account_info = schemas.AccountWithTransactions(
                account_number=account.number,
                bank=account.bank,
                transactions=[
                    schemas.Transaction.from_orm(transaction)
                    for transaction in account_transactions
                ]
            )
            result.append(account_info)

        return result

class RepositoryCard(RepositoryDB[models.Card, schemas.CardCreate, schemas.CardCreate]):  
    pass

class RepositoryCashback(
    RepositoryDB[models.Cashback, schemas.CashbackCreate, schemas.CashbackCreate]
):
    async def bulk_get(
        self, db: AsyncSession, cashbacks: List[schemas.Cashback]
    ) -> List[models.Cashback]:
        product_types = [
            cashback.product_type
            for cashback in cashbacks
        ]
        statement = select(self._model) \
            .filter(self._model.product_type.in_(product_types))

        results = await db.execute(statement=statement)
        return results.scalars().all()
    
class RepositoryUserCashback(
    RepositoryDB[models.UserCashback, schemas.UserCashbackCreate, schemas.UserCashbackUpdate]
):  
    async def filter_by(
        self,
        db: AsyncSession,
        with_cashbacks: bool = False,
        **kwargs
    ) -> List[models.UserCashback]:
        statement = select(self._model).filter_by(**kwargs)
        if with_cashbacks:
            statement = statement \
                .options(selectinload(self._model.cashback))
        results = await db.execute(statement=statement)
        lst = results.scalars().all()
        return lst
    
    # async def update(
    #     self,
    #     db: AsyncSession,
    #     obj_in: schemas.UserCashbackUpdate
    # ) -> models.UserCashback:
    #     db_obj: models.UserCashback = await self.get(
    #         db,
    #         id=obj_in.id
    #     )
    #     if db_obj:
    #         db_obj.status = obj_in.status
    #         await db.commit()
    #         await db.refresh(db_obj)
    #         return db_obj
    #     raise exceptions.UserCashbackDoesNotExist
    

class RepositoryTransaction(RepositoryDB[models.Transaction, schemas.TransactionCreate, schemas.TransactionCreate]):
    pass
    # async def bulk_create(
    #     self,
    #     db: AsyncSession,
    #     objs_in: List[schemas.TransactionCreate]
    # ) -> List[models.Transaction]:
    #     try:
    #         prepared_objs = []
    #         for obj in objs_in:
    #             obj = obj.dict()
    #             obj['time'] = obj['time'].replace(tzinfo=timezone.utc)
    #             prepared_objs.append(obj)

    #         db.add_all(prepared_objs)
    #         await db.commit()
    #         # await db.refresh(db_objs)
    #     except:
    #         await db.rollback()

user_crud = RepositoryUser(models.User)
account_crud = RepositoryAccount(models.Account)
card_crud = RepositoryCard(models.Card)
cashback_crud = RepositoryCashback(models.Cashback)
user_cashback_crud = RepositoryUserCashback(models.UserCashback)
transaction_crud = RepositoryTransaction(models.Transaction)