from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import ProductDAO


async def process_scraped_data(session: AsyncSession, brand_id: int, scraped_data: list):
    alerts = []
    changes_count = 0

    if not scraped_data:
        return alerts, 0

    scraped_data.sort(key=lambda x: x["Цена сейчас"])

    for item in scraped_data:
        article = int(item["Артикул"])
        current_price = item["Цена сейчас"]
        name = item["Наименование"]
        url = item["Ссылка"]

        # Ищем товар в нашей базе по артикулу
        product_in_db = await ProductDAO.find_one_or_none(session, article=article)

        if product_in_db is None:
            # СЦЕНАРИЙ 1: Нового товара нет в базе
            await ProductDAO.add(
                session,
                brand_id=brand_id,
                article=article,
                name=name,
                price=current_price,
                url=url
            )

            alerts.append(
                f"✨ <b>Новый товар!</b>\n"
                f"📦 {name}\n"
                f"💰 Цена: <b>{current_price} ₽</b>\n"
                f"🔗 <a href='{url}'>Открыть на WB</a>\n"
                f"--------------------------------"
            )
            changes_count += 1

        else:
            # СЦЕНАРИЙ 2: Товар уже есть в базе, проверяем цену
            old_price = product_in_db.price

            if current_price < old_price:
                # Цена СНИЗИЛАСЬ
                product_in_db.price = current_price  # Обновляем цену в объекте

                alerts.append(
                    f"📉 <b>Цена снижена!</b>\n"
                    f"📦 {name}\n"
                    f"💰 <s>{old_price}</s> → <b>{current_price} ₽</b>\n"
                    f"🔗 <a href='{url}'>Открыть на WB</a>\n"
                    f"--------------------------------"
                )
                changes_count += 1

            elif current_price > old_price:
                product_in_db.price = current_price

            # Если цена не изменилась, ничего не делаем

    await session.commit()

    return alerts, changes_count