from fastapi import FastAPI, Depends, HTTPException, Header, APIRouter
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "mysql+pymysql://{root}:{Maurya@1998}@localhost:3306/{dataviv}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


#<---------------------------------------------------------------------->
SECRET_KEY = "123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#<---------------------------------------------------------------------->



#<---------------------------------------------------------------------->
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)
#<---------------------------------------------------------------------->



#<---------------------------------------------------------------------->

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#<---------------------------------------------------------------------->


#<---------------------------------------------------------------------->

def create_token(data: dict, expires_delta: int):
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
#<---------------------------------------------------------------------->


#<---------------------------------------------------------------------->
router = APIRouter(prefix="/auth", tags=["Authentication"])

class AuthAPI:
    @staticmethod
    @router.post("/register")
    def register(user: UserCreate, db: Session = Depends(get_db)):
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_password = pwd_context.hash(user.password)
        new_user = User(username=user.username, password=hashed_password)
        db.add(new_user)
        db.commit()
        return {"message": "User registered successfully"}

    @staticmethod
    @router.post("/login")
    def login(user: UserLogin, db: Session = Depends(get_db)):
        existing_user = db.query(User).filter(User.username == user.username).first()

        if not existing_user or not pwd_context.verify(user.password, existing_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_token({"sub": existing_user.username}, ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_token({"sub": existing_user.username}, REFRESH_TOKEN_EXPIRE_DAYS * 1440)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    @router.get("/user-details")
    def get_user_details(authorization: str = Header(...), db: Session = Depends(get_db)):
        token = authorization.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user = db.query(User).filter(User.username == username).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return {"id": user.id, "username": user.username}

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

app.include_router(router)
#<---------------------------------------------------------------------->
