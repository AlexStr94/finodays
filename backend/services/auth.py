from datetime import datetime, timedelta
from typing import Annotated, List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from db.db import get_session
from exceptions.auth import CredentialException

from core.config import app_settings
from schemas import base as schemas
from models import base as models
from services.db import user_crud

SECRET_KEY = app_settings.secret_key
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_DAYS = 7


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_session),
) -> schemas.FullUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        gosuslugi_id: str = payload.get("sub")
        if gosuslugi_id is None:
            raise CredentialException
    except JWTError:
        raise CredentialException
    user_in_db: models.User | None = await user_crud.get(
        db=db,
        gosuslugi_id=gosuslugi_id
    )
    if user_in_db is None:
        raise CredentialException
    return schemas.FullUser(
        id=user_in_db.id,
        first_name=user_in_db.first_name,
        surname=user_in_db.surname,
        gosuslugi_id=user_in_db.gosuslugi_id,
        ebs=user_in_db.ebs
    )

async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> schemas.GosuslugiUser | None:
    """
    Заглушка для получения информации о
    пользователи с сайта госуслуг
    """
    counter = await user_crud.count_users(db)

    return schemas.GosuslugiUser(
        first_name='Иван',
        # middle_name='Иванович',
        surname=f'Иванов_{counter+1}',
        gosuslugi_id=str(counter+1),
        ebs=True
    )

def get_user_by_photo(photo)-> schemas.GosuslugiUser:
    return schemas.GosuslugiUser(
        first_name='Иван',
        # middle_name='Иванович',
        surname='Иванов_1',
        gosuslugi_id='1',
        ebs=True
    )


def get_cards(gosuslugi_id: str) -> List[schemas.LiteCard]:
    """
    Заглушка для получения информации о
    картах пользователя от банка
    """

    return [
        schemas.LiteCard(
            bank='Центр-инвест',
            card_number=f'1234567812345{gosuslugi_id}'
        ),
        schemas.LiteCard(
            bank='Тинькофф',
            card_number=f'1234567812545{gosuslugi_id}'
        ),
        schemas.LiteCard(
            bank='ВТБ',
            card_number=f'1234567812349{gosuslugi_id}'
        )
    ]
