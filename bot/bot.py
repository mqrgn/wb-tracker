import asyncio
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Твои новые модули
from app.dao import UserDAO, BrandDAO, SettingsDAO
from app.database import async_session_factory
from app.utils import generate_wb_url
from app.products_logic import process_scraped_data
from parser.wb_scraper import run_selenium_parser

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
scheduler = AsyncIOScheduler()


# --- ЛОГИКА ПРОВЕРКИ ---

async def run_check_for_user(session, setting):
    user_id = setting.user_id
    try:
        url = generate_wb_url(setting)
        # Получаем данные от парсера
        scraped_data = await asyncio.to_thread(run_selenium_parser, url)

        # Если парсер вернул None
        if scraped_data is None:
            await bot.send_message(user_id, "⚠️ Ошибка парсера. Попробуйте позже.")
            return

        # Проверяем цены
        alerts, count = await process_scraped_data(session, setting.brand_id, scraped_data)

        # Логика уведомлений
        if alerts:
            # Если есть новинки или скидки - шлем их
            await bot.send_message(user_id, f"✅ <b>Проверка завершена!</b>\nНайдено изменений: {count}")

            current_message = ""
            for alert in alerts:
                if len(current_message) + len(alert) > 4000:
                    await bot.send_message(user_id, current_message, link_preview_options={"is_disabled": True})
                    current_message = alert
                else:
                    current_message += alert + "\n"

            if current_message:
                await bot.send_message(user_id, current_message, link_preview_options={"is_disabled": True})

        else:
            # ВОТ ЭТОТ БЛОК ОТВЕЧАЕТ ЗА ПУСТУЮ СТРАНИЦУ:
            await bot.send_message(user_id,
                                   "✅ <b>Проверка завершена!</b>\nПо вашим фильтрам товаров не найдено или изменений нет.")

    except Exception as e:
        logging.error(f"Ошибка при проверке юзера {user_id}: {e}")


async def scheduled_task():
    """Глобальная проверка всех пользователей по расписанию"""
    logging.info("--- СТАРТ ГЛОБАЛЬНОЙ ПРОВЕРКИ ---")
    async with async_session_factory() as session:
        all_settings = await SettingsDAO.find_all(session)
        for setting in all_settings:
            await run_check_for_user(session, setting)
    logging.info("--- ГЛОБАЛЬНАЯ ПРОВЕРКА ЗАВЕРШЕНА ---")


# --- ХЭНДЛЕРЫ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    await message.answer(
        "👋 <b>Бот-монитор запущен!</b>\n\n"
        "Я проверяю цены в фоне и пришлю уведомление, если что-то изменится.\n"
        "Сейчас я настрою для тебя стандартные параметры и сделаю первый прогон..."
    )

    async with async_session_factory() as session:
        user = await UserDAO.find_one_or_none(session, user_id=user_id)
        if not user:
            # Регистрируем юзера
            await UserDAO.add(
                session,
                user_id=user_id,
                username=message.from_user.username,
                fullname=message.from_user.full_name
            )
            # Берем первый бренд и создаем дефолтные настройки
            brands = await BrandDAO.find_all(session)
            if brands:
                default_brand = brands[0]
                setting = await SettingsDAO.add(
                    session,
                    user_id=user_id,
                    brand_id=default_brand.brand_id,
                    min_price=0,
                    max_price=100000
                )
                # МГНОВЕННЫЙ ЗАПУСК парсера только для этого юзера
                # Используем create_task, чтобы не блокировать ответ бота
                asyncio.create_task(run_check_for_user(session, setting))
        else:
            await message.answer("С возвращением! Твои настройки уже в базе.")


@dp.message(Command("start_parser"))
async def cmd_manual_parser(message: types.Message):
    await message.answer("🚀 <b>Запуск проверки...</b>")
    async with async_session_factory() as session:
        setting = await SettingsDAO.find_one_or_none(session, user_id=message.from_user.id)
        if setting:
            await run_check_for_user(session, setting)
        else:
            await message.answer("Сначала нажми /start, чтобы создать профиль.")


# --- ЗАПУСК ---

async def main():
    # Запускаем планировщик
    scheduler.add_job(
        scheduled_task,
        "interval",
        minutes=30
    )
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот выключен")