import hashlib
import time
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User

router = APIRouter(prefix="/api/user", tags=["用户"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UpdateUserRequest(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_id: int, username: str) -> str:
    timestamp = str(int(time.time()))
    raw = f"{user_id}{username}{timestamp}"
    return hashlib.md5(raw.encode()).hexdigest()


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
    }


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    try:
        existing = db.query(User).filter(User.username == req.username).first()
        if existing:
            return {"code": 400, "message": "用户名已存在", "data": None}

        user = User(
            username=req.username,
            password=hash_password(req.password),
            nickname=req.nickname,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "code": 200,
            "message": "注册成功",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "nickname": user.nickname,
            },
        }
    except Exception as e:
        db.rollback()
        return {"code": 500, "message": f"注册失败: {str(e)}", "data": None}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == req.username).first()
        if not user:
            return {"code": 404, "message": "用户不存在", "data": None}

        if user.password != hash_password(req.password):
            return {"code": 401, "message": "密码错误", "data": None}

        token = generate_token(user.id, user.username)

        return {
            "code": 200,
            "message": "登录成功",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "token": token,
            },
        }
    except Exception as e:
        return {"code": 500, "message": f"登录失败: {str(e)}", "data": None}


@router.get("/info/{user_id}")
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"code": 404, "message": "用户不存在", "data": None}

        return {"code": 200, "message": "获取用户信息成功", "data": user_to_dict(user)}
    except Exception as e:
        return {"code": 500, "message": f"获取用户信息失败: {str(e)}", "data": None}


@router.put("/info/{user_id}")
def update_user_info(user_id: int, req: UpdateUserRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"code": 404, "message": "用户不存在", "data": None}

        if req.nickname is not None:
            user.nickname = req.nickname
        if req.avatar is not None:
            user.avatar = req.avatar

        db.commit()
        db.refresh(user)

        return {"code": 200, "message": "更新用户信息成功", "data": user_to_dict(user)}
    except Exception as e:
        db.rollback()
        return {"code": 500, "message": f"更新用户信息失败: {str(e)}", "data": None}
