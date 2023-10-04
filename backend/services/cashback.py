from datetime import date, datetime
from typing import List

from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from cashbacker.casbacker import Cashbacker
from models import base as models
from schemas import base as schemas


def can_choose_cashback(account: models.Account) -> bool:
    if account.bank == 'Центр-инвест':
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
    df = pd.DataFrame([(d.time, d.value, d.category) for d in transactions], 
                  columns=['time', 'value', 'category'])

    # временная заглушка
    CASHBACK_CATEGORIES = [
        'автозапчасти', 'видеоигры', 'напитки', 'продукты питания',
        'закуски и приправы', 'аквариум', 'одежда', 'уборка',
        'электроника', 'образование'
    ]
    return [
        schemas.Cashback(
            product_type=CASHBACK_CATEGORIES[i],
            value=i+1
        )
        for i in range(6)
    ]
    if can_choose_cashback(account):
        return Cashbacker(account).calculate_cashback_categories()

    return None
