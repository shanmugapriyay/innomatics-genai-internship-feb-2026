🏨 Hotel Room Booking System API

This project is a backend application built using FastAPI that manages hotel room details and booking operations.

🚀 Overview

The API allows users to:

Browse available hotel rooms
Make and manage bookings
Perform check-in and check-out actions
Search, filter, and sort room data
Navigate results using pagination

It demonstrates how real-world booking systems work on the backend.

🛠️ Technologies Used
Python
FastAPI
Uvicorn
Pydantic

Create virtual environment:
python -m venv venv

Activate:

Windows:
venv\Scripts\activate
Step 3: Install dependencies
pip install -r requirements.txt
Step 4: Run the application
uvicorn main:app --reload
🌐 API Testing

Access interactive API docs:

👉 http://127.0.0.1:8000/docs

📌 Core Functionalities
Room Operations
View all rooms
Retrieve room by ID
Add, update, and delete rooms
Booking Operations
Create booking
View all bookings
Perform check-in and check-out
Advanced Features
Filter rooms based on type, price, and availability
Search rooms using keywords
Sort results dynamically
Implement pagination
Combined browsing (search + sort + pagination)