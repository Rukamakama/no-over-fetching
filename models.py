from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase, Mapped, mapped_column
from typing import List

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./order_management.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Models
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    
    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")

class Address(Base):
    __tablename__ = "addresses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    zipcode: Mapped[str]
    country: Mapped[str]
    
    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="address")

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[str]
    
    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(default="pending")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    product: Mapped["Product"] = relationship("Product", back_populates="orders")
    address: Mapped["Address"] = relationship("Address", back_populates="orders")

# Model registry for dynamic access
MODELS = {
    'orders': Order,
    'users': User,
    'addresses': Address,
    'products': Product
}

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()