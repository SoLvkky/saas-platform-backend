from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.config import settings
from app.core.security import hash_token, create_access_token, generate_refresh_token
from app.db.session import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    token, refresh_token = await AuthService.authenticate_user(
        db,
        data.email,
        data.password
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return TokenResponse(access_token=token, refresh_token=refresh_token)

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }

@router.post("/refresh")
async def refresh(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    token_hash = hash_token(refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
        )
    )

    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(status_code=401)
    
    if db_token.revoked:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == db_token.family_id)
            .values(revoked=True)
        )
        await db.commit()

        raise HTTPException(status_code=401)
    
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401)
    
    db_token.revoked = True

    new_refresh = generate_refresh_token()

    new_token = RefreshToken(
        user_id=db_token.user_id,
        token_hash=hash_token(new_refresh),
        family_id=db_token.family_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.TOKEN_EXPIRE)
    )

    db.add(new_token)
    await db.commit()
    
    access = create_access_token(str(db_token.user_id))

    return {
        "access_token": access,
        "refresh_token": new_refresh
    }

@router.post("/logout")
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    
    token_hash = hash_token(refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    db_token = result.scalar_one_or_none()

    if not db_token:
        return {"status": "ok"}
    
    db_token.revoked = True
    await db.commit()

    return {"status": "ok"}

@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == current_user.id)
        .values(revoked=True)
    )

    await db.commit()

    return {"status": "ok"}