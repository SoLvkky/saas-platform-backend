import uuid

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import verify_password, create_access_token, generate_refresh_token, hash_token
from app.models.user import User
from app.models.refresh_token import RefreshToken

class AuthService:

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> str:
        
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        token = create_access_token(subject=str(user.id))
        refresh_token = await create_refresh_token(db, user.id)

        return token, refresh_token
    
async def create_refresh_token(db, user_id):

    family_id = uuid.uuid4()

    token = generate_refresh_token()

    db_token = RefreshToken()

    db_token.user_id = user_id
    db_token.token_hash = hash_token(token)
    db_token.family_id = family_id
    db_token.expires_at = datetime.now(timezone.utc) + timedelta(days=settings.TOKEN_EXPIRE)

    db.add(db_token)
    await db.commit()

    return token