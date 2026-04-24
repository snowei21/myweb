from fastapi import FastAPI

# models
import models
from database import engine
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ลงทะเบียน static folder (CSS, JS, Images, Fonts)
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

# ลงทะเบียน templates folder
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")


# routers
from api import router
app.include_router(router)


# main page
from fastapi import Request
from fastapi.responses import HTMLResponse

# localhost:8000/
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(name='index.html', request=request, context={
        "message": "Hello World",
        "score": 76,
        "activities": ["Running", "Football", "Badminton"]
    })


# =============
# แสดงข้อมูลสินค้า
# =============
from database import SessionLocal
from models import Product, Category

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import shutil
import os

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/products", response_class=HTMLResponse)
def product_list(request: Request):
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        return templates.TemplateResponse(name="product_list.html", request=request, context={
            "products": products
        })
    finally:
        db.close()

@app.get("/products/create", response_class=HTMLResponse)
def create_form(request: Request):
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return templates.TemplateResponse(name="product_form.html", request=request,context={
            "categories": categories
    })
    finally:
        db.close()


@app.post("/products/create")
def create_product(
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(None)
):
    db = SessionLocal()

    filename = None
    if image:
        filename = image.filename
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    product = Product(
        name=name,
        price=price,
        category_id=category_id,
        image=filename
    )

    db.add(product)
    db.commit()
    db.close()

    return RedirectResponse("/products", status_code=303)


@app.get("/products/edit/{id}", response_class=HTMLResponse)
def edit_form(request: Request, id: int):
    db = SessionLocal()
    try:
        product = db.get(Product, id)
        categories = db.query(Category).all()
        return templates.TemplateResponse(name="product_form.html", request=request, context={
            "product": product,
            "categories": categories
        })
    finally:
        db.close()


@app.post("/products/edit/{id}")
def update_product(
    id: int,
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(None)
):
    db = SessionLocal()
    product = db.get(Product, id)

    product.name = name
    product.price = price
    product.category_id = category_id

    if image and image.filename:
        filename = image.filename
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        product.image = filename

    db.commit()
    db.close()
    return RedirectResponse("/products", status_code=303)


@app.get("/products/delete/{id}")
def delete_product(id: int):
    db = SessionLocal()
    product = db.get(Product, id)
    db.delete(product)
    db.commit()
    db.close()
    return RedirectResponse("/products", status_code=303)

#
# Date Time
#
from datetime import datetime

@app.get("/api/servertime")
def get_datetime():
    return {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


#
# product search
#
@app.get("/products/search", response_class=HTMLResponse)
def product_search(request: Request):
    return templates.TemplateResponse(name="product_search.html", request=request, context={
        "request": request,
    })


@app.get("/api/products/search")
def product_search_api(search: str = ""):
    db = SessionLocal()
    try:
        return db.query(Product).filter(
            Product.name.like(f"%{search}%")
        ).all()
    finally:
        db.close()


#
# Upload slip & OCR
#
@app.get("/pvs/upload", response_class=HTMLResponse)
def pvs_upload(request: Request):
    return templates.TemplateResponse(name="pvs_upload.html", request=request, context={
        "request": request,
    })


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

import easyocr
import re

reader = easyocr.Reader(['th','en'])


def parse_thai_datetime(text):
    thai_months = {
        "ม.ค.": 1, "ก.พ.": 2, "มี.ค.": 3,
        "เม.ย.": 4, "พ.ค.": 5, "มิ.ย.": 6,
        "ก.ค.": 7, "ส.ค.": 8, "ก.ย.": 9,
        "ต.ค.": 10, "พ.ย.": 11, "ธ.ค.": 12
    }

    match = re.search(
        r'(\d{1,2})\s+([^\s]+)\s+(\d{2})(?:.*?(\d{1,2}):(\d{2}))?',
        text
    )

    if not match:
        raise ValueError("Invalid date format")

    day = int(match.group(1))
    month = thai_months.get(match.group(2), 1)
    year_ad = int(match.group(3)) + 2500 - 543

    time_match = re.search(r'(\d{1,2}):(\d{2})', text)
    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    return datetime(year_ad, month, day, hour, minute)

def process_ocr(image_path):
    result = reader.readtext(image_path)
    text = " ".join([r[1] for r in result])
    # Extract amount
    amount_match = re.search(r'\d+\.\d{2}', text)
    amount = float(amount_match.group()) if amount_match else 0
    # Extract date
    date_match = parse_thai_datetime(text)
    return {
        "text": text,
        "amount": amount,
        "datetime": date_match,
    }


@app.post("/api/pvs/upload-ocr")
async def upload_ocr(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = process_ocr(filepath)
    return result


#
#
#
from models import Order
from datetime import timedelta

@app.get("/api/pvs/orders")
def get_orders():
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        return [
            {
                "id": o.id,
                "order_no": o.order_no,
                "amount_total": o.amount_total,
                "order_date": str(o.order_date),
                "state": o.state
            }
            for o in orders
        ]
    finally:
        db.close()


@app.post("/api/pvs/verify-slip")
async def verify_slip(data: dict):
    amount = data["amount"]
    paid_at = datetime.strptime(data["datetime"], "%Y-%m-%dT%H:%M:%S")
    start = paid_at - timedelta(minutes=10)
    end = paid_at + timedelta(minutes=10)

    db = SessionLocal()

    orders = db.query(Order).filter(
        Order.amount_total == amount,
        Order.order_date >= start,
        Order.order_date <= end,
        Order.state == "Draft"
    ).all()

    return [
        {
            "id": o.id,
            "order_no": o.order_no,
            "amount_total": o.amount_total,
            "order_date": str(o.order_date)
        }
        for o in orders
    ]


@app.post("/api/pvs/mark-paid")
def mark_paid(data: dict):
    order_ids = data.get("order_ids", [])
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(Order.id.in_(order_ids)).all()
        for o in orders:
            o.state = "Paid"
        db.commit()
        return {"status": "success"}
    finally:
        db.close()


@app.get('/api/hello')
def hello_api():
    return {'message': 'API Works!'}

@app.get('/api/grade')
def grade_api(score:float = None):
    if score >= 85:
        return {'grade': 'A'}
    elif score >= 75 and score < 85:
        return {'grade': 'B'}
    return {'grade': 'F'}