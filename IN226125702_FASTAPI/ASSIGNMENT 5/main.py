from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="My E-commerce Store API - Day 6")

# ── Product Data ──────────────────────────────────────────────
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook",       "price": 99,  "category": "Stationery",  "in_stock": True},
    {"id": 3, "name": "USB Hub",        "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set",        "price": 49,  "category": "Stationery",  "in_stock": True},
]

orders   = []
feedback = []

# ── Helper ────────────────────────────────────────────────────
def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None

# ── Pydantic Models ───────────────────────────────────────────
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id:    int = Field(..., gt=0)
    quantity:      int = Field(..., gt=0, le=50)


# ══════════════════════════════════════════════════════════════
# BASIC ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}

@app.get("/orders")
def get_all_orders():
    return {"orders": orders, "total_orders": len(orders)}

@app.post("/orders")
def place_order(order: OrderRequest):
    product = next((p for p in products if p["id"] == order.product_id), None)
    if not product:
        return {"error": "Product not found"}
    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}
    order_id = len(orders) + 1
    new_order = {
        "order_id":      order_id,
        "customer_name": order.customer_name,
        "product":       product["name"],
        "quantity":      order.quantity,
        "total_price":   product["price"] * order.quantity,
        "status":        "confirmed",
    }
    orders.append(new_order)
    return {"message": "Order placed successfully", "order": new_order}


# ══════════════════════════════════════════════════════════════
# Q1 — GET /products/search — Search by keyword (case-insensitive)
# ══════════════════════════════════════════════════════════════

@app.get("/products/search")
def search_products(keyword: str = Query(..., description="Search keyword")):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {
        "keyword":     keyword,
        "total_found": len(results),
        "products":    results,
    }


# ══════════════════════════════════════════════════════════════
# Q2 — GET /products/sort — Sort by price or name
# ══════════════════════════════════════════════════════════════

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price", description="Sort by: price or name"),
    order:   str = Query("asc",   description="Order: asc or desc"),
):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}
    reverse = (order == "desc")
    result  = sorted(products, key=lambda p: p[sort_by], reverse=reverse)
    return {
        "sort_by":  sort_by,
        "order":    order,
        "products": result,
        "total":    len(result),
    }


# ══════════════════════════════════════════════════════════════
# Q3 — GET /products/page — Paginate products
# ══════════════════════════════════════════════════════════════

@app.get("/products/page")
def get_products_paged(
    page:  int = Query(1, ge=1,  description="Page number"),
    limit: int = Query(2, ge=1, le=20, description="Items per page"),
):
    total       = len(products)
    total_pages = -(-total // limit)   # ceiling division
    start       = (page - 1) * limit
    paged       = products[start: start + limit]
    return {
        "page":        page,
        "limit":       limit,
        "total":       total,
        "total_pages": total_pages,
        "products":    paged,
    }


# ══════════════════════════════════════════════════════════════
# Q4 — GET /orders/search — Search orders by customer name
# ══════════════════════════════════════════════════════════════

@app.get("/orders/search")
def search_orders(customer_name: str = Query(..., description="Customer name to search")):
    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]
    if not results:
        return {"message": f"No orders found for: {customer_name}"}
    return {
        "customer_name": customer_name,
        "total_found":   len(results),
        "orders":        results,
    }


# ══════════════════════════════════════════════════════════════
# Q5 — GET /products/sort-by-category — Sort by category then price
# ══════════════════════════════════════════════════════════════

@app.get("/products/sort-by-category")
def sort_by_category():
    result = sorted(products, key=lambda p: (p["category"], p["price"]))
    return {"products": result, "total": len(result)}


# ══════════════════════════════════════════════════════════════
# Q6 — GET /products/browse — Search + Sort + Paginate in one
# ══════════════════════════════════════════════════════════════

@app.get("/products/browse")
def browse_products(
    keyword: str = Query(None,    description="Search keyword"),
    sort_by: str = Query("price", description="Sort by: price or name"),
    order:   str = Query("asc",   description="Order: asc or desc"),
    page:    int = Query(1,  ge=1,      description="Page number"),
    limit:   int = Query(4,  ge=1, le=20, description="Items per page"),
):
    # Step 1: Search
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # Step 2: Sort
    if sort_by in ["price", "name"]:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order == "desc"))

    # Step 3: Paginate
    total       = len(result)
    total_pages = -(-total // limit)
    start       = (page - 1) * limit
    paged       = result[start: start + limit]

    return {
        "keyword":     keyword,
        "sort_by":     sort_by,
        "order":       order,
        "page":        page,
        "limit":       limit,
        "total_found": total,
        "total_pages": total_pages,
        "products":    paged,
    }


# ══════════════════════════════════════════════════════════════
# BONUS — GET /orders/page — Paginate orders list
# ══════════════════════════════════════════════════════════════

@app.get("/orders/page")
def get_orders_paged(
    page:  int = Query(1, ge=1,      description="Page number"),
    limit: int = Query(3, ge=1, le=20, description="Orders per page"),
):
    start = (page - 1) * limit
    return {
        "page":        page,
        "limit":       limit,
        "total":       len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders":      orders[start: start + limit],
    }


# ══════════════════════════════════════════════════════════════
# GET single product — MUST be after all fixed routes above
# ══════════════════════════════════════════════════════════════

@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    return {"product": product}
