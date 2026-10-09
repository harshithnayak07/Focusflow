from app.database.connection import Sessionlocal
from fastapi import Depends

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()