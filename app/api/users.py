from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.register(
        email=user_in.email,
        hashed_password=hash_password(user_in.password)
    )
    return user