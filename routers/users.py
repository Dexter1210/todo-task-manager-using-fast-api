from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserRead, UserUpdate
from auth import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/users/", response_model=UserRead, responses={400: {"description": "Email already registered", "content": {"application/json": {"example": {"detail": "Email already registered"}}}}})
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=user.email, name=user.name, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/{user_id}", response_model=UserRead, responses={404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}}})
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}", responses={404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}}})
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

@router.put("/users/{user_id}", response_model=UserRead, responses={404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}}})
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email is not None:
        db_user.email = user.email
    if user.name is not None:
        db_user.name = user.name
    if user.password is not None:
        db_user.hashed_password = user.password
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == form.username) | (User.name == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # JWT expects things to be in string
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}