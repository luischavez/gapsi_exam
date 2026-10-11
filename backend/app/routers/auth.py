from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, FirestoreDB
from app.internal.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, Token, User

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login')
async def login(data: LoginRequest, db: FirestoreDB) -> Token:
    """
    Try to login with the given credentials or raise an exception
    :param data: credentials
    :param db: database
    :return:
    """
    doc = await db.collection('users').document(data.username).get()
    user = doc.to_dict() if doc.exists else None

    if user is None or not verify_password(data.password, user['password_hash']):
        # return the same exception to both cases to avoid security issues
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    return Token(access_token=create_access_token(data.username))

@router.get('/user')
async def me(user: CurrentUser) -> User:
    return user
