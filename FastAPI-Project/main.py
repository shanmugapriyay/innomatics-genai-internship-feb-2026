from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from collections import Counter

app = FastAPI()

# ---------------- Q2 DATA ----------------
rooms = [
    {"id": 1, "room_number": "101", "type": "Single", "price_per_night": 1000, "floor": 1, "is_available": True},
    {"id": 2, "room_number": "102", "type": "Double", "price_per_night": 2000, "floor": 1, "is_available": True},
    {"id": 3, "room_number": "200", "type": "Suite", "price_per_night": 4000, "floor": 2, "is_available": False},
    {"id": 4, "room_number": "202", "type": "Deluxe", "price_per_night": 3000, "floor": 2, "is_available": True},
    {"id": 5, "room_number": "301", "type": "Suite", "price_per_night": 5000, "floor": 3, "is_available": True},
    {"id": 6, "room_number": "302", "type": "Single", "price_per_night": 1200, "floor": 3, "is_available": True}
]

bookings = []
booking_counter = 1

# ---------------- Q6 MODEL ----------------
class BookingRequest(BaseModel):
    guest_name: str = Field(..., min_length=2)
    room_id: int = Field(..., gt=0)
    nights: int = Field(..., gt=0, le=30)
    phone: str = Field(..., min_length=10)
    meal_plan: str = "none"
    early_checkout: bool = False

class NewRoom(BaseModel):
    room_number: str = Field(..., min_length=1)
    type: str = Field(..., min_length=2)
    price_per_night: int = Field(..., gt=0)
    floor: int = Field(..., gt=0)
    is_available: bool = True

# ---------------- HELPERS (Q7) ----------------
def find_room(room_id):
    return next((r for r in rooms if r["id"] == room_id), None)

def calculate_stay_cost(price, nights, meal, early_checkout):
    extra = 0
    if meal == "breakfast":
        extra = 500
    elif meal == "all-inclusive":
        extra = 1200

    base = (price + extra) * nights
    discount = 0

    if early_checkout:
        discount = base * 0.1

    return base, discount, base - discount

def filter_rooms_logic(type=None, max_price=None, floor=None, is_available=None):
    result = []
    for r in rooms:
        if type and r["type"].lower() != type.lower():
            continue
        if max_price and r["price_per_night"] > max_price:
            continue
        if floor and r["floor"] != floor:
            continue
        if is_available is not None and r["is_available"] != is_available:
            continue
        result.append(r)
    return result

# ---------------- Q1 ----------------
@app.get("/")
def home():
    return {"message": "Welcome to Grand Stay Hotel"}

# ---------------- Q2 ----------------
@app.get("/rooms")
def get_rooms():
    total = len(rooms)
    available = sum(1 for r in rooms if r["is_available"])
    return {"total": total, "available_count": available, "rooms": rooms}

# ---------------- Q5 (IMPORTANT ORDER) ----------------
@app.get("/rooms/summary")
def summary():
    prices = [r["price_per_night"] for r in rooms]
    available = sum(1 for r in rooms if r["is_available"])
    type_count = dict(Counter(r["type"] for r in rooms))

    return {
        "total_rooms": len(rooms),
        "available": available,
        "occupied": len(rooms) - available,
        "cheapest": min(prices),
        "costliest": max(prices),
        "type_breakdown": type_count
    }
# ---------------- Q19 ----------------
@app.get("/bookings/search")
def search_booking(name: str):
    result = [b for b in bookings if name.lower() in b["guest_name"].lower()]
    return {"count": len(result), "bookings": result}

@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "total_cost"):
    return {"bookings": sorted(bookings, key=lambda x: x[sort_by])}

# ---------------- Q20 ----------------
@app.get("/rooms/browse")
def browse(keyword: str = None, sort_by: str = "price_per_night", order: str = "asc", page: int = 1, limit: int = 3):
    result = rooms

    if keyword:
        result = [r for r in result if keyword.lower() in r["room_number"].lower() or keyword.lower() in r["type"].lower()]

    reverse = order == "desc"
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    total = len(result)
    start = (page-1)*limit
    end = start+limit

    return {
        "total": total,
        "total_pages": (total+limit-1)//limit,
        "rooms": result[start:end]
    }

# ---------------- Q16 ----------------
@app.get("/rooms/search")
def search_rooms(keyword: str):
    result = [r for r in rooms if keyword.lower() in r["room_number"].lower() or keyword.lower() in r["type"].lower()]
    if not result:
        return {"message": "No rooms found"}
    return {"total_found": len(result), "rooms": result}

# ---------------- Q17 ----------------
@app.get("/rooms/sort")
def sort_rooms(sort_by: str = "price_per_night", order: str = "asc"):
    valid = ["price_per_night", "floor", "type"]
    if sort_by not in valid:
        raise HTTPException(400, "Invalid field")

    reverse = order == "desc"
    return {"rooms": sorted(rooms, key=lambda x: x[sort_by], reverse=reverse)}

# ---------------- Q18 ----------------
@app.get("/rooms/page")
def paginate(page: int = 1, limit: int = 2):
    start = (page-1)*limit
    end = start+limit
    total = len(rooms)

    return {
        "total": total,
        "total_pages": (total+limit-1)//limit,
        "rooms": rooms[start:end]
    }

# ---------------- Q10 ----------------
@app.get("/rooms/filter")
def filter_rooms(
    type: str = Query(None),
    max_price: int = Query(None),
    floor: int = Query(None),
    is_available: bool = Query(None)
):
    result = filter_rooms_logic(type, max_price, floor, is_available)
    return {"count": len(result), "rooms": result}

# ---------------- Q3 ----------------
@app.get("/rooms/{room_id}")
def get_room(room_id: int):
    room = find_room(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    return room

# ---------------- Q4 ----------------
@app.get("/bookings")
def get_bookings():
    return {"total": len(bookings), "bookings": bookings}

# ---------------- Q8 + Q9 ----------------
@app.post("/bookings")
def create_booking(req: BookingRequest):
    global booking_counter

    room = find_room(req.room_id)
    if not room:
        raise HTTPException(404, "Room not found")

    if not room["is_available"]:
        raise HTTPException(400, "Room occupied")

    base, discount, final = calculate_stay_cost(
        room["price_per_night"],
        req.nights,
        req.meal_plan,
        req.early_checkout
    )

    room["is_available"] = False

    booking = {
        "booking_id": booking_counter,
        "guest_name": req.guest_name,
        "room_number": room["room_number"],
        "type": room["type"],
        "nights": req.nights,
        "meal_plan": req.meal_plan,
        "discount": discount,
        "total_cost": final,
        "status": "confirmed"
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# ---------------- Q10 ----------------
@app.get("/rooms/filter")
def filter_rooms(
    type: str = Query(None),
    max_price: int = Query(None),
    floor: int = Query(None),
    is_available: bool = Query(None)
):
    result = filter_rooms_logic(type, max_price, floor, is_available)
    return {"count": len(result), "rooms": result}

# ---------------- Q11 ----------------
@app.post("/rooms", status_code=201)
def add_room(room: NewRoom):
    for r in rooms:
        if r["room_number"] == room.room_number:
            raise HTTPException(400, "Duplicate room number")

    new = {"id": len(rooms)+1, **room.dict()}
    rooms.append(new)
    return new

# ---------------- Q12 ----------------
@app.put("/rooms/{room_id}")
def update_room(room_id: int, price_per_night: int = None, is_available: bool = None):
    room = find_room(room_id)
    if not room:
        raise HTTPException(404, "Room not found")

    if price_per_night is not None:
        room["price_per_night"] = price_per_night
    if is_available is not None:
        room["is_available"] = is_available

    return room

# ---------------- Q13 ----------------
@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    room = find_room(room_id)
    if not room:
        raise HTTPException(404, "Room not found")

    if not room["is_available"]:
        raise HTTPException(400, "Room is occupied")

    rooms.remove(room)
    return {"message": "Deleted"}

# ---------------- Q14 ----------------
@app.post("/checkin/{booking_id}")
def checkin(booking_id: int):
    for b in bookings:
        if b["booking_id"] == booking_id:
            b["status"] = "checked_in"
            return b
    raise HTTPException(404, "Booking not found")

# ---------------- Q15 ----------------
@app.post("/checkout/{booking_id}")
def checkout(booking_id: int):
    for b in bookings:
        if b["booking_id"] == booking_id:
            b["status"] = "checked_out"

            # free room
            for r in rooms:
                if r["room_number"] == b["room_number"]:
                    r["is_available"] = True

            return b
    raise HTTPException(404, "Booking not found")

@app.get("/bookings/active")
def active_bookings():
    result = [b for b in bookings if b["status"] in ["confirmed", "checked_in"]]
    return {"count": len(result), "bookings": result}

