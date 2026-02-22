from fastapi import APIRouter, HTTPException, Request,FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.config.db import db

router= APIRouter()
templates = Jinja2Templates(directory="templates")
# app=FastAPI()
 
@router.get("/admin/dashboard")
async def admin_dashboard(request: Request):


    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=302)

    # Stats
    total_users = len(
        db.table("profile").select("*").eq("Role", "user").execute().data
    )

    total_vendors = len(
        db.table("profile").select("*").eq("Role", "vendor").execute().data
    )

    total_halls = len(
        db.table("functionhalls").select("*").execute().data
    )

    total_bookings = len(
        db.table("bookings").select("*").execute().data
    )

    # Only pending halls
    pending_halls = db.table("functionhalls") \
        .select("*") \
        .eq("status", "pending") \
        .execute().data
    
    for hall in pending_halls:
        vendor = db.table("profile") \
            .select("Name") \
            .eq("userid", hall["vendor_id"]) \
            .execute().data

        hall["vendor_name"] = vendor[0]["Name"] if vendor else "Unknown"

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "total_users": total_users,
        "total_vendors": total_vendors,
        "total_halls": total_halls,
        "total_bookings": total_bookings,
        "pending_halls": pending_halls
    })



@router.get("/vendor/dashboard")
async def vendor_dashboard(request: Request):

    user_id = request.session.get("user_id")

    halls = db.table("functionhalls") \
        .select("*") \
        .eq("vendor_id", user_id) \
        .execute().data

    return templates.TemplateResponse("vendor_dashboard.html", {
        "request": request,
        "halls": halls
    })


@router.get("/user/dashboard")
async def user_dashboard(request: Request):

    # if request.session.get("role") != "user":
    #     return RedirectResponse("/login", status_code=302)

    halls = db.table("functionhalls") \
        .select("*") \
        .eq("status", "approved") \
        .execute().data
    
    role = request.session.get("role")
    message = request.query_params.get("msg")

    return templates.TemplateResponse("user_dashboard.html", {
        "request": request,
        "halls": halls,
        "message": message,
        "role":role
    })



@router.get("/approve-hall/{hall_id}")
async def approve_hall(hall_id: int, request: Request):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=302)

    db.table("functionhalls") \
        .update({"status": "approved"}) \
        .eq("id", hall_id) \
        .execute()

    return RedirectResponse("/admin/dashboard", status_code=302)


@router.get("/reject-hall/{hall_id}")
async def reject_hall(hall_id: int, request: Request):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=302)

    db.table("functionhalls") \
        .update({"status": "rejected"}) \
        .eq("id", hall_id) \
        .execute()

    return RedirectResponse("/admin/dashboard", status_code=302)


@router.get("/admin/manage-users")
async def manage_users(request: Request):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=302)

    users = db.table("profile") \
        .select("*") \
        .eq("Role", "user") \
        .execute().data

    return templates.TemplateResponse("manage_users.html", {
        "request": request,
        "users": users
    })

@router.get("/admin/manage-vendors")
async def manage_vendors(request: Request):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=302)

    vendors = db.table("profile") \
        .select("*") \
        .eq("Role", "vendor") \
        .execute().data

    return templates.TemplateResponse("manage_vendors.html", {
        "request": request,
        "vendors": vendors
    })


@router.get("/admin/view-bookings")
async def view_bookings(request: Request):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=302)

    # 🔹 Step 1: Get all users
    users = db.table("profile") \
        .select("userid, Name") \
        .execute().data

    user_map = {user["userid"]: user["Name"] for user in users}

    # 🔹 Step 2: Get all halls
    halls = db.table("functionhalls") \
        .select("id, name") \
        .execute().data

    hall_map = {hall["id"]: hall["name"] for hall in halls}

    # 🔹 Step 3: Get all bookings
    bookings = db.table("bookings") \
        .select("*") \
        .execute().data

    # 🔹 Step 4: Attach names manually
    for booking in bookings:
        booking["user_name"] = user_map.get(booking["user_id"], "Unknown")
        booking["hall_name"] = hall_map.get(booking["hall_id"], "Unknown")

    return templates.TemplateResponse("admin_bookings.html", {
        "request": request,
        "bookings": bookings
    })

