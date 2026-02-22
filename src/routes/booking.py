from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.config.db import db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/book/{hall_id}")
async def book_hall(request: Request, hall_id: int):

    user_id = request.session.get("user_id")

    db.table("bookings").insert({
        "user_id": user_id,
        "hall_id": hall_id,
        "status": "booked"
    }).execute()

    return RedirectResponse("/user/dashboard", status_code=303)


@router.post("/book-hall")
async def book_hall(
    request: Request,
    hall_id: int = Form(...),
    event_date: str = Form(...)
):
    
    if request.session.get("role") != "user":
        return RedirectResponse("/login", status_code=302)

    user_id = request.session.get("user_id")

    # Check only approved or pending bookings
    existing = db.table("bookings") \
        .select("*") \
        .eq("hall_id", hall_id) \
        .eq("event_date", event_date) \
        .in_("status", ["pending", "approved"]) \
        .execute().data

    if existing:
        return RedirectResponse(
            "/user/dashboard?msg=Hall already booked for this date",
            status_code=302
        )

    db.table("bookings").insert({
        "user_id": user_id,
        "hall_id": hall_id,
        "event_date": event_date,
        "status": "pending"
    }).execute()

    return RedirectResponse(
        "/user/dashboard?msg=Booking request sent to vendor",
        status_code=302
    )



@router.get("/my-bookings")
async def my_bookings(request: Request):

    if request.session.get("role") != "user":
        return RedirectResponse("/login", status_code=302)

    user_id = request.session.get("user_id")

    bookings = db.table("bookings") \
    .select("*, functionhalls(name)") \
    .eq("user_id", user_id) \
    .execute().data

    return templates.TemplateResponse("my_bookings.html", {
        "request": request,
        "bookings": bookings
    })


@router.post("/check-availability")
async def check_availability(
    request: Request,
    hall_id: int = Form(...),
    event_date: str = Form(...)
):

    existing = db.table("bookings") \
        .select("*") \
        .eq("hall_id", hall_id) \
        .eq("event_date", event_date) \
        .execute().data

    if existing:
        return RedirectResponse("/user/dashboard?msg=not_available", status_code=302)

    return RedirectResponse("/user/dashboard?msg=available", status_code=302)


@router.get("/approve-booking/{booking_id}")
async def approve_booking(booking_id: int, request: Request):

    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    db.table("bookings") \
        .update({"status": "approved"}) \
        .eq("id", booking_id) \
        .execute()

    return RedirectResponse("/vendor-bookings", status_code=302)


@router.get("/reject-booking/{booking_id}")
async def reject_booking(booking_id: int, request: Request):

    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    db.table("bookings") \
        .update({"status": "rejected"}) \
        .eq("id", booking_id) \
        .execute()

    return RedirectResponse("/vendor-bookings", status_code=302)

