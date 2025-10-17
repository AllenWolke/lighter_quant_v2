"""
认证路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from core.security import authenticate_user, create_access_token, get_current_active_user
from models.user import User
from schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建新用户
    from core.security import get_password_hash
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


from pydantic import BaseModel
from typing import Union
from fastapi import Body

class LoginRequestJSON(BaseModel):
    """JSON格式的登录请求"""
    username: str
    password: str


@router.post("/login")
async def login(
    credentials: LoginRequestJSON,
    db: Session = Depends(get_db)
):
    """用户登录（JSON 格式）"""
    
    # 从凭据获取用户名和密码
    username = credentials.username
    password = credentials.password
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少用户名或密码",
        )
    
    # 验证用户
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 返回响应（同时提供两种命名格式以兼容前后端）
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "fullName": user.full_name,  # 驼峰命名（前端）
        "full_name": user.full_name,  # 下划线命名（兼容）
        "isActive": user.is_active,
        "is_active": user.is_active,
        "isSuperuser": user.is_superuser,
        "is_superuser": user.is_superuser
    }
    
    return {
        "accessToken": access_token,  # 驼峰命名（前端期望）
        "access_token": access_token,  # 下划线命名（兼容）
        "tokenType": "bearer",
        "token_type": "bearer",
        "user": user_data
    }


@router.post("/login/form")
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录（OAuth2 表单格式）"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return current_user
