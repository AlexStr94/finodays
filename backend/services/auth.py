from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import app_settings
from db.db import get_session
from exceptions.auth import CredentialException
from models import base as models
from schemas import base as schemas
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
