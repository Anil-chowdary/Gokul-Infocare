from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

app = FastAPI()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Template setup
templates = Jinja2Templates(directory="templates")


# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String, unique=True)
    email_id = Column(String, unique=True)
    address = Column(String)


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/submit/")
def create_user(
        request: Request,
        first_name: str = Form(...),
        last_name: str = Form(...),
        phone_number: str = Form(...),
        email_id: str = Form(...),
        address: str = Form(...),
        db: Session = Depends(get_db)  # Fixing dependency injection for the database
):
    if len(phone_number) != 10 or not phone_number.isdigit():
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid phone number"})

    new_user = User(first_name=first_name, last_name=last_name, phone_number=phone_number, email_id=email_id,
                    address=address)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return templates.TemplateResponse("index.html", {"request": request, "message": "User created successfully!"})


@app.get("/users/", response_class=HTMLResponse)
def get_users(request: Request, db: Session = Depends(get_db)):  # Fixing dependency injection for the database
    users = db.query(User).all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

