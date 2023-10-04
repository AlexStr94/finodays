from fastapi import HTTPException, status


class AuthError(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = 'Incorrect username or password',
        headers: dict = {"WWW-Authenticate": "Bearer"}
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )


class AntiSpoofingException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = 'Пользователь не распознан на фото',
        headers: dict = {"WWW-Authenticate": "Bearer"}
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )


class EBSExceptin(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = 'Пользователь не найден в системе ЕБС',
        headers: dict = {"WWW-Authenticate": "Bearer"}
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )


class CredentialException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = 'Could not validate credentials',
        headers: dict = {"WWW-Authenticate": "Bearer"}
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )