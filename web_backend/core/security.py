"""
安全认证和权限管理
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt  # 直接使用 bcrypt，避免 passlib 兼容性问题
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from models.user import User

# JWT认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（使用 bcrypt 直接验证）"""
    try:
        # 确保密码和哈希都是正确的格式
        if not isinstance(plain_password, str):
            plain_password = str(plain_password)
        if not isinstance(hashed_password, str):
            hashed_password = str(hashed_password)
        
        # 截断密码为 72 字节
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        
        # 使用 bcrypt 验证
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"密码验证错误: {e}")
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希（使用 bcrypt 直接生成）
    
    Args:
        password: 原始密码字符串
        
    Returns:
        BCrypt 哈希后的密码
        
    Note:
        BCrypt 限制密码最多 72 字节。会自动截断超过此长度的密码。
    """
    # 确保密码是字符串类型
    if not isinstance(password, str):
        password = str(password)
    
    # 移除可能的前后空格
    password = password.strip()
    
    # 截断密码为 72 字节（bcrypt 限制）
    password_bytes = password.encode('utf-8')[:72]
    
    # 使用 bcrypt 直接生成哈希
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # 返回字符串格式
    return hashed.decode('utf-8')


def authenticate_user(db: Session, username: str, password: str):
    """验证用户"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户账户已禁用")
    return current_user
