from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 密钥
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Token 续期阈值：当 token 剩余有效期小于此值时自动续期（分钟）
TOKEN_REFRESH_THRESHOLD_MINUTES = 5

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """
    验证 token 并返回用户信息
    返回: (user_id, should_refresh) 元组，should_refresh 表示是否需要续期 token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None, False
        
        # 检查 token 是否需要续期
        exp_timestamp = payload.get("exp")
        should_refresh = False
        if exp_timestamp:
            exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
            remaining_time = exp_datetime - datetime.utcnow()
            # 如果剩余时间小于阈值，标记需要续期
            if remaining_time < timedelta(minutes=TOKEN_REFRESH_THRESHOLD_MINUTES):
                should_refresh = True
        
        return int(user_id), should_refresh
    except JWTError:
        return None, False