import asyncio
import os

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import BrandDAO, SettingsDAO
from app.database import get_db
from app.schemas import SBrand, SSettings, SSettingsAdd
from bot.bot import dp, bot

app = FastAPI()

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Authorization", "Access-Control-Allow-Origin"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Для теста через ngrok, чтобы не вылезало постоянно окно авторизации
@app.middleware("http")
async def add_ngrok_skip_header(request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "1"
    return response


@app.get("/")
async def read_index():
    return FileResponse("app/static/index.html")


@app.get("/brands", response_model=list[SBrand])
async def get_brands(session: AsyncSession = Depends(get_db)):
    brands = await BrandDAO.find_all(session=session)
    return brands


@app.get("/settings/{user_id}", response_model=SSettings)
async def get_user_settings(user_id: int, session: AsyncSession = Depends(get_db)):
    settings = await SettingsDAO.find_one_or_none(session, user_id=user_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")
    return settings


@app.post("/settings")
async def save_settings(data: SSettingsAdd, session: AsyncSession = Depends(get_db)):
    # Ищем существующую запись
    existing = await SettingsDAO.find_one_or_none(session, user_id=data.user_id)

    if existing:
        # Обновляем (если нашли)
        await SettingsDAO.update(
            session,
            instance_id=existing.id,
            brand_id=data.brand_id,
            min_price=data.min_price,
            max_price=data.max_price
        )
    else:
        # Добавляем (если не нашли)
        await SettingsDAO.add(
            session,
            user_id=data.user_id,
            brand_id=data.brand_id,
            min_price=data.min_price,
            max_price=data.max_price
        )

    # Коммитим изменения в базу
    await session.commit()

    return {"status": "ok"}


async def run_fastapi():
    # Запуск uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # Запускаем две задачи одновременно: FastAPI и Bot Polling
    await asyncio.gather(
        run_fastapi(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Проект остановлен")