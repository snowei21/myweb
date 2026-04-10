from pydantic import BaseModel


class ProductSchema(BaseModel):
    name: str
    price: float
    category_id: int

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    price: float
    category_id: int
