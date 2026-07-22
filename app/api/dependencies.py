from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        payload = decode_access_token(token)
        user_id: Any = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=401, detail='Invalid token')
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')

    return {'id': user_id}
