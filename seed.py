from database import SessionLocal, engine, Base
from models import Category, Product, Order
from datetime import datetime

db = SessionLocal()


def reset_database():
    print("Droping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)


def run_seed():
    db.add_all([
        Category(name='นิยาย'),
        Category(name='การ์ตูน'),
        Category(name='เกษตร'),
        Category(name='คอมพิวเตอร์'),
    ])
    db.commit()

    db.add_all([
        Product(name='เดอะลอร์ดออฟเดอะริงส์', price=100, category_id=1),
        Product(name='ซึบาสะ', price=200, category_id=2),
        Product(name='สร้าง Frontend ด้วย Next.js', price=300, category_id=4),
        Product(name='เรียนรู้การทำ API ด้วย FastAPI', price=400, category_id=4),
    ])
    db.commit()

    db.add_all([
        Order(
            order_no="X001",
            amount_total=200,
            order_date=datetime(2021, 7, 10, 15, 10),
            state="Draft"
        ),
        Order(
            order_no="X002",
            amount_total=200,
            order_date=datetime(2021, 7, 10, 15, 25),
            state="Draft"
        ),
        Order(
            order_no="X003",
            amount_total=500,
            order_date=datetime(2021, 7, 10, 16, 0),
            state="Draft"
        ),
    ])
    db.commit()

if __name__ == "__main__":
    reset_database()
    run_seed()
