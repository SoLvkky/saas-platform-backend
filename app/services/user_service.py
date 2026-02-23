from app.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, email: str, hashed_password: str):
        existing = await self.repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        return await self.repo.create(email, hashed_password)