from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.dependencies import get_db
from app.api.users import router as users_router

app = FastAPI()
app.include_router(users_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db": result.scalar()}