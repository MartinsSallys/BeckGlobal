from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db

router = APIRouter()


@router.get('/health')
async def health(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        db_status = 'ok'
    except Exception:
        db_status = 'unavailable'

    return {'status': 'ok', 'database': db_status}
