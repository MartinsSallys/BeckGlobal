from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db

router = APIRouter()


@router.get('/health')
def health(response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text('SELECT 1'))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {'status': 'error', 'database': 'unavailable'}

    return {'status': 'ok', 'database': 'ok'}
