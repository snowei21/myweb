from fastapi import APIRouter
from database import SessionLocal
from models import Product

router = APIRouter()


@router.get('/api/test')
def api_test():
    return {'message': 'Hello API!'}


@router.get('/api/products')
def api_product_list():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        return products
    finally:
        db.close()
