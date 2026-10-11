from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.cloud.firestore import AsyncClient

from app.database import get_db
from app.internal.security import decode_access_token
from app.schemas.auth import User

FirestoreDB = Annotated[AsyncClient, Depends(get_db)]

bearer_schema = HTTPBearer()
HTTPBearerCredentials = Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)]

async def get_current_user(
        bearer: HTTPBearerCredentials,
        db: FirestoreDB,
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid or expired token',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    username = decode_access_token(bearer.credentials)
    if username is None:
        raise unauthorized

    doc = await db.collection('users').document(username).get()
    if not doc.exists:
        raise unauthorized

    return User(username=username)

CurrentUser = Annotated[User, Depends(get_current_user)]
