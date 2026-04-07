from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.utils.jwt import verify_token, create_access_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)

# 存储需要刷新的token信息（用于在路由中设置响应头）
refresh_token_info = {}

# 获取当前用户
def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    logger.info(f"get_current_user 被调用")
    logger.info(f"Request headers: {dict(request.headers)}")

    # 尝试从Authorization header获取token
    token = None
    if credentials:
        token = credentials.credentials
        logger.info(f"从HTTPBearer获取到token: {token[:20]}...")
    else:
        # 如果HTTPBearer没有获取到，尝试直接从header获取
        auth_header = request.headers.get("Authorization")
        logger.info(f"Authorization header: {auth_header}")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            logger.info(f"从header直接获取到token: {token[:20]}...")

    if not token:
        logger.error("未找到token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id, should_refresh = verify_token(token)
    logger.info(f"验证token结果: user_id={user_id}, should_refresh={should_refresh}")

    # 如果token需要续期，生成新token并存储在请求状态中
    if should_refresh and user_id:
        new_token = create_access_token(data={"sub": str(user_id)})
        # 使用request.state存储新token，以便在路由中设置响应头
        request.state.new_token = new_token
        logger.info(f"token已续期，新token: {new_token[:20]}...")
    
    if user_id is None:
        logger.error("token验证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error(f"用户不存在: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"成功获取用户: {user.username}")
    return user

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserSchema)
def update_me(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.username:
        current_user.username = user_update.username
    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        from app.utils.password import get_password_hash
        current_user.password_hash = get_password_hash(user_update.password)
    db.commit()
    db.refresh(current_user)
    return current_user

# 管理员路由
@router.get("/", response_model=list[UserSchema])
def get_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    users = db.query(User).offset(skip).limit(limit).all()
    return users