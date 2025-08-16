from sqlalchemy.orm import Session
from models import SessionLocal, User, Address, Product, Order

def init_database():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already initialized")
            return
        
        # Create sample users
        users = [
            User(id=1, username="john_doe", email="john@example.com"),
            User(id=2, username="jane_smith", email="jane@example.com"),
            User(id=3, username="peter_cane", email="peter@example.com")
        ]
        db.add_all(users)
        
        # Create sample addresses
        addresses = [
            Address(id=1, zipcode="12345", country="USA"),
            Address(id=2, zipcode="54321", country="Canada"),
            Address(id=3, zipcode="98765", country="Japan")
        ]
        db.add_all(addresses)
        
        # Create sample products
        products = [
            Product(id=1, name="Laptop", price="999.99"),
            Product(id=2, name="Mouse", price="29.99"),
            Product(id=3, name="Keyboard", price="199.99"),
            Product(id=4, name="Headphones", price="99.99"),
            Product(id=5, name="Phone", price="99.99")
        ]
        db.add_all(products)
        
        # Create sample orders
        orders = [
            Order(id=1, status="pending", user_id=1, product_id=1, address_id=1),
            Order(id=2, status="pending", user_id=2, product_id=2, address_id=2),
            Order(id=3, status="pending", user_id=1, product_id=3, address_id=1),
            Order(id=4, status="pending", user_id=2, product_id=4, address_id=2),
            Order(id=5, status="pending", user_id=3, product_id=5, address_id=3)
        ]
        db.add_all(orders)
        
        db.commit()
        print("Database initialized with sample data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()