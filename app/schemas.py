from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator, Field


# --- User schemas ---
class SUser(BaseModel):
    user_id: int
    username: Optional[str] = None
    fullname: str

    model_config = ConfigDict(from_attributes=True)


# --- Brand schemas ---
class SBrand(BaseModel):
    brand_id: int
    name: str
    url: str

    model_config = ConfigDict(from_attributes=True)


# --- Settings schemas ---
class SSettingsAdd(BaseModel):
    user_id: int
    brand_id: int
    min_price: int = Field(ge=0, default=0)
    max_price: int = Field(ge=0, default=100000)

    @model_validator(mode='after')
    def check_prices(self) -> 'SSettingsAdd':
        if self.min_price >= self.max_price:
            raise ValueError("Минимальная цена не может быть больше или равна максимальной")
        return self


class SSettings(SSettingsAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Product schemas ---
class SProduct(BaseModel):
    brand_id: int
    article: int
    name: str
    price: int
    url: str

    model_config = ConfigDict(from_attributes=True)