from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.organization import User, Organization
from app.schemas.schemas import UserLogin, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or user.password_hash != user_in.password: # For demo simplicity / hash in prod
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "access_token": f"token-{user.id}",
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "organization_id": user.organization_id
        }
    }

@router.get("/me")
def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
