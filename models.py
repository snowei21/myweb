from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(200), nullable=True)
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Category")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_no = Column(String(50))
    order_date = Column(DateTime)
    amount_total = Column(Float)
    state = Column(String(50))  # Draft, Paid, Cancel
