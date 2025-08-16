from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from models import get_db, Order, Product, Address
from utils import parse_params_api, fields_to_query_api


def list_orders(fields: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List orders with optional field selection.
    
    Examples:
    - /orders (returns all default fields)
    - /orders?fields=id,status (returns only id and status)
    - /orders?fields=orders{id,status,users{username},products{name},addresses{zipcode}}
    """
    if fields:
        try:
            parsed_fields = parse_params_api(fields)
            return fields_to_query_api(db, "orders", parsed_fields)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing fields: {str(e)}")
    else:
        # Default behavior - return basic order information
        orders = db.query(Order).all()
        return [
            {
                "id": order.id,
                "status": order.status,
                "user_id": order.user_id,
                "product_id": order.product_id,
                "address_id": order.address_id
            }
            for order in orders
        ]


def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order.id,
        "status": order.status,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "address_id": order.address_id
    }


def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price
    }


def get_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id).first()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return {
        "id": address.id,
        "zipcode": address.zipcode,
        "country": address.country
    }