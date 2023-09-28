from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_204_NO_CONTENT,
        detail: str = 'User with this id doesn\'t exist'
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail
        )


class AccountNotFoundException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_204_NO_CONTENT,
        detail: str = 'Account with this params doesn\'t exist'
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail
        )