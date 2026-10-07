from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.database import users_collection
from app.utils import hash_password, verify_password

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ---------------- Register Page ----------------
@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request}
    )


# ---------------- Register User ----------------
@router.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):

    username = username.strip()
    email = email.strip().casefold()
    if not username or len(username) > 80 or len(password) < 8:
        raise HTTPException(status_code=422, detail="Use a name up to 80 characters and a password of at least 8 characters.")

    try:
        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hash_password(password),
        })
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Email already exists")
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Authentication service is temporarily unavailable")

    return RedirectResponse(
        url="/login?registered=true",
        status_code=303
    )


# ---------------- Login Page ----------------
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):

    registered = request.query_params.get("registered")

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "registered": registered
        }
    )


# ---------------- Login ----------------
@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    try:
        user = users_collection.find_one({"email": email.strip().casefold()})
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Authentication service is temporarily unavailable")

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Save username in session
    request.session["username"] = user["username"]

    # Redirect to chatbot
    return RedirectResponse(
        url="/chatbot",
        status_code=303
    )


# ---------------- Logout ----------------
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url="/login",
        status_code=303
    )
