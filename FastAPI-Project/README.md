# 🏨 Grand Stay Hotel Booking API

A complete **FastAPI-based backend project** for managing hotel rooms and bookings.

---

## 🚀 Features

* Room Management (CRUD)
* Booking System
* Check-in / Check-out Workflow
* Filtering, Searching, Sorting
* Pagination
* Combined Browse API

---

## 🛠️ Tech Stack

* Python
* FastAPI
* Uvicorn
* Pydantic



### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

* Windows:

```bash
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run Server

```bash
uvicorn main:app --reload
```

---

## 🌐 API Documentation

Open in browser:

👉 http://127.0.0.1:8000/docs

---

## 📌 Sample API Usage

### 🔹 Get All Rooms

```
GET /rooms
```

### 🔹 Create Booking

```
POST /bookings
```

### 🔹 Check-in

```
POST /checkin/{booking_id}
```


