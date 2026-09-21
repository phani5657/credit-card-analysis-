from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserResponse , TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix ="/users", tags = ["users"])

@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400,detail="Email already registered")
    new_user = User( name=user.name, email=user.email,password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model = TokenResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user:
        raise HTTPException(status_code=401,detail="Invalid email or password")

    if not verify_password(user.password,existing_user.password_hash):
        raise HTTPException(status_code=401,detail="Invalid email or password")

    access_token = create_access_token(data={"user_id": existing_user.id})

    return {"access_token": access_token,"token_type": "bearer"}

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/me", response_model = UserResponse)
def get_me(current_user_id: int = Depends(get_current_user),db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user_id).first()

    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user

@router.get("/{user_id}",response_model=UserResponse)
def get_user(user_id: int,current_user_id: int = Depends(get_current_user),db: Session = Depends(get_db)):
    if current_user_id != user_id:
        raise HTTPException(status_code=403,detail="You are not allowed to access this user")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user

@router.put( "/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user: UserUpdate,current_user_id: int = Depends(get_current_user),db: Session = Depends(get_db)):
    
    if current_user_id != user_id:
        raise HTTPException(status_code=403,detail="You are not allowed to update this user")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    if updated_user.name is not None:
        user.name = updated_user.name

    if updated_user.email is not None:
        existing_user = db.query(User).filter(User.email == updated_user.email).first()

        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400,detail="Email already registered")
        user.email = updated_user.email

    db.commit()
    db.refresh(user)

    return user

@router.delete(
    "/{user_id}"
)
def delete_user(user_id: int,current_user_id: int = Depends(get_current_user),db: Session = Depends(get_db)):
   
    if current_user_id != user_id:
        raise HTTPException(status_code=403,detail="You are not allowed to delete this user")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }