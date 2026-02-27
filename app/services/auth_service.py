from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import verify_password, create_access_token

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
        return token