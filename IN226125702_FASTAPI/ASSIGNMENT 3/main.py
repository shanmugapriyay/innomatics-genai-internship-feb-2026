# Import required libraries
from fastapi import FastAPI, Response, status, Query
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI()

# Initial product data
products = [
    {"id": 1, "name": "Keyboard", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

# Pydantic model for new product
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


# Helper function to find product by ID
def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


# ---------------------------------------------------------
# Q1: POST /products
# Add a new product and prevent duplicate product names
# ---------------------------------------------------------
@app.post("/products")
def add_product(product: NewProduct, response: Response):

    # Check duplicate name
    for p in products:
        if p["name"].lower() == product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product already exists"}

    # Generate new ID
    next_id = max(p["id"] for p in products) + 1

    # Create product dictionary
    new_product = {
        "id": next_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    # Add to product list
    products.append(new_product)

    response.status_code = status.HTTP_201_CREATED
    return {"message": "Product added", "product": new_product}


# ---------------------------------------------------------
# Q4: GET /products
# View all products
# ---------------------------------------------------------
@app.get("/products")
def get_products():

    return {
        "products": products,
        "total": len(products)
    }


# ---------------------------------------------------------
# Q5: GET /products/audit
# Inventory summary
# ---------------------------------------------------------
@app.get("/products/audit")
def product_audit():

    # Products in stock
    in_stock_list = [p for p in products if p["in_stock"]]

    # Products out of stock
    out_stock_list = [p for p in products if not p["in_stock"]]

    # Calculate stock value (assume 10 units each)
    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    # Find most expensive product
    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }


# ---------------------------------------------------------
# BONUS: PUT /products/discount
# Apply discount to category
# ---------------------------------------------------------
@app.put("/products/discount")
def bulk_discount(
    category: str = Query(...),
    discount_percent: int = Query(..., ge=1, le=99)
):

    updated = []

    for p in products:
        if p["category"] == category:
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"message": f"No products found in category: {category}"}

    return {
        "message": f"{discount_percent}% discount applied",
        "updated_count": len(updated),
        "updated_products": updated
    }


# ---------------------------------------------------------
# Q2: PUT /products/{product_id}
# Update price or stock status
# ---------------------------------------------------------
@app.put("/products/{product_id:int}")
def update_product(
    product_id: int,
    price: int | None = None,
    in_stock: bool | None = None,
    response: Response = None
):

    product = find_product(product_id)

    # Product not found
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    # Update price
    if price is not None:
        product["price"] = price

    # Update stock
    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}


# ---------------------------------------------------------
# Q3: DELETE /products/{product_id}
# Delete a product
# ---------------------------------------------------------
@app.delete("/products/{product_id:int}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    # Remove product
    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}