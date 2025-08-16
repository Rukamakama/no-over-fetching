from fastapi import FastAPI
from routes import list_orders, get_order, get_product, get_address

# FastAPI app
app = FastAPI(title="Order Management API")

# Register routes
app.get("/orders")(list_orders)
app.get("/orders/{order_id}")(get_order)
app.get("/products/{product_id}")(get_product)
app.get("/addresses/{address_id}")(get_address)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)