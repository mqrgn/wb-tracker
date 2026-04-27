import asyncio
from app.database import get_db
from app.dao import BrandDAO


async def seed_brands():
    initial_brands = [
        {"name": "samsung", "url": "https://www.wildberries.ru/wbrands/brands/samsung?"},
        {"name": "apple", "url": "https://www.wildberries.ru/wbrands/brands/apple?"},
        {"name": "asus", "url": "https://www.wildberries.ru/wbrands/brands/asus?"},
    ]

    async for session in get_db():
        # Проверяем, есть ли уже бренды в базе
        existing_brands = await BrandDAO.find_all(session=session)

        if not existing_brands:
            print("База пуста. Наполняю брендами...")
            for brand_data in initial_brands:
                await BrandDAO.add(session=session, **brand_data)
            print("Готово!")
        else:
            print("Бренды уже есть в базе. Пропускаю.")
        break


if __name__ == "__main__":
    asyncio.run(seed_brands())