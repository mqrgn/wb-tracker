from app.models import Settings


def generate_wb_url(settings: Settings):
    low_price = settings.min_price * 100
    high_price = settings.max_price * 100

    params = f"priceU={low_price}%3B{high_price}&sort=popular&xsubject=515%3B2290&page=1"

    return f"{settings.brand.url}{params}"
