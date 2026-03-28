from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# -----------------------------
# In-memory Data
# -----------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 299, "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True}
]

cart = []
orders = []
order_id_counter = 1


# -----------------------------
# Helper Functions
# -----------------------------

def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def calculate_subtotal(product, quantity):
    return product["price"] * quantity


def calculate_grand_total():
    return sum(item["subtotal"] for item in cart)


# -----------------------------
# Models
# -----------------------------

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# -----------------------------
# Endpoints
# -----------------------------


# Question 1:
# Add items to cart (Wireless Mouse and Notebook)
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    product = find_product(product_id)

    # Question 3:
    # Handle product not found (404)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Question 3:
    # Handle out-of-stock product (400)
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    # Question 4:
    # If product already exists in cart, update quantity
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_subtotal(product, item["quantity"])

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    # Question 1:
    # Add new product to cart
    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_subtotal(product, quantity)
    }

    cart.append(new_item)

    return {
        "message": "Added to cart",
        "cart_item": new_item
    }


# Question 2:
# View cart and verify total
@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": calculate_grand_total()
    }


# Question 5:
# Remove item from cart
@app.delete("/cart/{product_id}")
def remove_item(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed"}

    raise HTTPException(status_code=404, detail="Item not found in cart")


# Question 5 and Question 6:
# Checkout and create orders
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    global order_id_counter

    # Bonus:
    # Handle empty cart checkout
    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    placed_orders = []

    # Question 6:
    # Create one order per cart item
    for item in cart:
        order = {
            "order_id": order_id_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        placed_orders.append(order)

        order_id_counter += 1

    grand_total = calculate_grand_total()

    # Question 5:
    # Clear cart after checkout
    cart.clear()

    return {
        "message": "Order placed successfully",
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }


# Question 5 and Question 6:
# View all orders
@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }