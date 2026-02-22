from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.config.db import db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Show Add Hall Page
@router.get("/add-hall")
async def add_hall_page(request: Request):

    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse("addhall.html", {"request": request})



@router.post("/add-hall")
async def add_hall(
    request: Request,
    name: str = Form(...),
    price: int = Form(...),
    image: str = Form(...),
    location: str = Form(...),
    ambience: str = Form(...)
):
    
    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)
    
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login", status_code=302)

    db.table("functionhalls").insert({
        "name": name,
        "price": price,
        "image": image,
        "location":location,
        "ambience": ambience,
        "vendor_id": user_id,
        "status": "pending"
    }).execute()

    return RedirectResponse("/vendor/dashboard", status_code=303)


@router.get("/delete-hall/{hall_id}")
async def delete_hall(request: Request, hall_id: int):

    # ✅ Allow only vendor
    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    # ✅ Get vendor id from session
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login", status_code=302)

    # ✅ Delete only if hall belongs to this vendor
    db.table("functionhalls") \
        .delete() \
        .eq("id", hall_id) \
        .eq("vendor_id", user_id) \
        .execute()

    return RedirectResponse("/vendor/dashboard", status_code=303)


@router.get("/vendor/bookings")
async def vendor_bookings(request: Request):

    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    vendor_id = request.session.get("user_id")

    # Step 1: Get vendor halls
    halls = db.table("functionhalls") \
        .select("id, name, image") \
        .eq("vendor_id", vendor_id) \
        .execute().data

    hall_map = {hall["id"]: hall for hall in halls}
    hall_ids = list(hall_map.keys())

    if not hall_ids:
        bookings = []
    else:
        bookings = db.table("bookings") \
            .select("*") \
            .in_("hall_id", hall_ids) \
            .execute().data

        # Get all user IDs from bookings
        user_ids = list(set([booking["user_id"] for booking in bookings]))

        users = db.table("profile") \
            .select("userid, Name") \
            .in_("userid", user_ids) \
            .execute().data

        user_map = {user["userid"]: user["Name"] for user in users}

        # Attach hall & user details manually
        for booking in bookings:
            booking["hall_name"] = hall_map[booking["hall_id"]]["name"]
            booking["hall_image"] = hall_map[booking["hall_id"]]["image"]
            booking["user_name"] = user_map.get(booking["user_id"], "Unknown")

    return templates.TemplateResponse("vendor_bookings.html", {
        "request": request,
        "bookings": bookings
    })




@router.get("/vendor/approve-booking/{booking_id}")
async def approve_booking(request: Request, booking_id: int):

    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    db.table("bookings") \
        .update({"status": "approved"}) \
        .eq("id", booking_id) \
        .execute()

    return RedirectResponse("/vendor/bookings", status_code=302)


@router.get("/vendor/reject-booking/{booking_id}")
async def reject_booking(request: Request, booking_id: int):

    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    db.table("bookings") \
        .update({"status": "rejected"}) \
        .eq("id", booking_id) \
        .execute()

    return RedirectResponse("/vendor/bookings", status_code=302)



@router.get("/edit-hall/{hall_id}")
async def edit_hall_page(request: Request, hall_id: int):

    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    user_id = request.session.get("user_id")

    hall = db.table("functionhalls") \
        .select("*") \
        .eq("id", hall_id) \
        .eq("vendor_id", user_id) \
        .execute().data

    if not hall:
        return RedirectResponse("/vendor/dashboard", status_code=302)

    return templates.TemplateResponse("edit_hall.html", {
        "request": request,
        "hall": hall[0]
    })



@router.post("/update-hall/{hall_id}")
async def update_hall(
    request: Request,
    hall_id: int,
    name: str = Form(...),
    price: int = Form(...),
    image: str = Form(...),
    location: str = Form(...),
    ambience: str = Form(...)
):

    if request.session.get("role") != "vendor":
        return RedirectResponse("/login", status_code=302)

    user_id = request.session.get("user_id")

    db.table("functionhalls") \
        .update({
            "name": name,
            "price": price,
            "image": image,
            "location": location,
            "ambience": ambience
        }) \
        .eq("id", hall_id) \
        .eq("vendor_id", user_id) \
        .execute()

    return RedirectResponse("/vendor/dashboard", status_code=302)


