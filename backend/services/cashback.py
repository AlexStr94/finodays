import asyncio
from datetime import date, datetime
from typing import List

from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from cashbacker.casbacker import cashbacker
from models import base as models
from schemas import base as schemas


def can_choose_cashback(bank: str) -> bool:
    if bank == 'Центр-инвест':
        return True

    return False


async def get_card_choose_cashback(
        db: AsyncSession, account: models.Account, month: date
    ) -> List[schemas.Cashback]:
    from services.db import transaction_crud
    from services.external_integrations import update_account_transactions

    await update_account_transactions(
        db=db,
        account=account
    )

    start_time = datetime.combine(
        month, datetime.min.time()
    ) - relativedelta(year=2)

    transactions: List[models.Transaction] = await transaction_crud \
        .get_user_transactions_from(
            db=db, account_id=account.id, start_time=start_time
        )
    df = pd.DataFrame([(d.time, 'клиент', d.category, d.value) for d in transactions], 
                  columns=['date', 'client', 'topic', 'price'])
    
    cashbacks = await asyncio.to_thread(
        cashbacker.cashbaks_for_user, data=df
    )

    return [
        schemas.Cashback(
            product_type=row['topics'],
            value=row['percent']
        )
        for _, row in cashbacks.iterrows()
    ]

