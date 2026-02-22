from fastapi import APIRouter, HTTPException, Request, Form,FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.config.db import db
 
templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get('/')
def home():
    return RedirectResponse('/user/dashboard')
 
# @router.get('/')
# def home():
#     return RedirectResponse('/login')

@router.get("/signup")
def show_signup_page(request:Request):
    return templates.TemplateResponse("signup.html",{"request":request})
 
 

 
@router.post("/signup")
def signup(
    request:Request,
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    name=Form(...)
):
    if role not in ["user", "vendor"]:
        raise HTTPException(status_code=400, detail="Invalid role")
 
    result = db.auth.sign_up({
        "email": email,
        "password": password
    })
 
    if not result.user:
        raise HTTPException(status_code=400, detail="Signup failed")
    user_id = result.user.id
    # print(user_id)
 
    db.table("profile").insert({
        "userid": result.user.id,
        "Name":name,
        "email": email,
        "Role": role
    }).execute()
 
    request.session["user_id"] = result.user.id
    request.session["role"] = role

    if role == "vendor":
        return RedirectResponse("/vendor/dashboard", status_code=302)
    else:
        return RedirectResponse("/user/dashboard", status_code=302)
 
    # response = RedirectResponse(redirect_url, status_code=302)
    # response.set_cookie(
    #     key="session",
    #     value=result.session.access_token,
    #     max_age=3600,
    #     httponly=True
    # )
    # return response
 
    
 
 
@router.get('/login')
def login(request: Request):
    return templates.TemplateResponse("login.html", { 'request': request})
 
 
@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    result = db.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
 
    if not result.user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
 

    role_data = db.table("profile").select("Role").eq("email", email).execute()
    role = role_data.data[0]["Role"]

    request.session["user_id"] = result.user.id
    request.session["role"] = role
 
    if role == "admin":
        return RedirectResponse("/admin/dashboard", status_code=302)
    elif role == "vendor":
        return RedirectResponse("/vendor/dashboard", status_code=302)
    else:
        return RedirectResponse("/user/dashboard", status_code=302)

    # return RedirectResponse(redirect_url, status_code=302)

 
 
# @router.post('/admin/login')
# def api_login(request: Request, email = Form(...), password = Form(...)):
#     result = db.auth.sign_in_with_password({
#         'email': email,
#         'password': password
#     })
#     print(result.user.email)
 
#     if result.user:
#         if result.user.email == "met@gmail.com":
#             response =  RedirectResponse('/admin/dashboard', status_code=302)
#             response.set_cookie('user_session', result.session.access_token, max_age=3600)
#             return response
#     raise HTTPException(status_code=401, detail="Invalid admin credentials")
 
# @router.post("/user/login")
# def user_login(
#     request: Request,
#     email: str = Form(...),
#     password: str = Form(...)
# ):
#     result = db.auth.sign_in_with_password({
#         "email": email,
#         "password": password
#     })
 
#     if result.user:
#         response = RedirectResponse("/user/dashboard", status_code=302)
#         response.set_cookie(
#             key="user_session",
#             value=result.session.access_token,
#             max_age=3600,
#             httponly=True
#         )
#         return response
    
#     raise HTTPException(status_code=401, detail="Invalid user credentials")
 
# @router.post("/vendor/login")
# def vendor_login(
#     request: Request,
#     email: str = Form(...),
#     password: str = Form(...)
# ):
#     result = db.auth.sign_in_with_password({
#         "email": email,
#         "password": password
#     })
 
#     if result.user:
#         response = RedirectResponse("/vendor/dashboard", status_code=302)
#         response.set_cookie(
#             key="vendor_session",
#             value=result.session.access_token,
#             max_age=3600,
#             httponly=True
#         )
#         return response
 
#     raise HTTPException(status_code=401, detail="Invalid user credentials")
 
 
 
# @router.get("/admin/dashboard")
# def show_signup_page(request:Request):
#     return templates.TemplateResponse("admin_dashboard.html",{"request":request})
 
 
# @router.get("/vendor/dashboard")
# def vendor_dashboard(request: Request):

#     if request.session.get("role") != "vendor":
#         return RedirectResponse("/login", status_code=302)

#     return templates.TemplateResponse("vendor_dashboard.html", {"request": request})

 
# @router.get("/user/dashboard")
# def show_signup_page(request:Request):
#     return templates.TemplateResponse("user_dashboard.html",{"request": request})

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)