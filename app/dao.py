from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import User, Brand, Settings, Product


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add(cls, session: AsyncSession, **data):
        instance = cls.model(**data)
        session.add(instance)
        await session.commit()
        return instance

    @classmethod
    async def update(cls, session: AsyncSession, instance_id: int, **data):
        query = select(cls.model).filter_by(id=instance_id)
        result = await session.execute(query)
        instance = result.scalar_one_or_none()

        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            await session.commit()
        return instance


class UserDAO(BaseDAO):
    model = User


class BrandDAO(BaseDAO):
    model = Brand


class ProductDAO(BaseDAO):
    model = Product


class SettingsDAO(BaseDAO):
    model = Settings

    # Переопределяем методы специально для настроек
    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by):
        query = (
            select(cls.model)
            .filter_by(**filter_by)
            .options(joinedload(cls.model.brand))
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = (
            select(cls.model)
            .filter_by(**filter_by)
            .options(joinedload(cls.model.brand))
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
