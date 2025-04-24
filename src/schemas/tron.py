from datetime import datetime
from typing import Annotated, Any

from base58 import b58decode_check
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    conint,
    field_validator,
)


class TronAddressQueryRequest(BaseModel):
    address: str

    @field_validator("address")
    @classmethod
    def validate_address(cls, value):
        if not isinstance(value, str):
            raise ValueError("Value is not str")

        # Базовые проверки
        if len(value) != 34:
            raise ValueError("Len(value) != 34")

        if not value.startswith("T"):
            raise ValueError("Address starts not with T")

        # Проверка символов (Base58)
        try:
            decoded = b58decode_check(value)
            # Декодированный адрес (без checksum) должен быть 21 байт (1 байт версии + 20 байт публичного ключа)
            if len(decoded) != 21:
                raise ValueError("Decoded address len != 21")

        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid address format: {str(e)}")
        return value


class TronAddressQueryResponse(BaseModel):
    address: str = Field(description="TRON address")
    bandwidth_used: int = Field(description="Used bandwidth")
    bandwidth_limit: int = Field(description="Total bandwidth limit")
    energy_used: int | None = Field(description="Used energy")
    energy_limit: int | None = Field(description="Total energy limit")
    trx_balance: float = Field(description="TRX balance in TRX")


class TronAQRecordsRequest(BaseModel):
    page_number: Annotated[int, conint(strict=True, ge=1)] = 1
    page_size: Annotated[int, conint(strict=True, ge=1)] = 100


class TronAQRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    address: str
    address_data: dict[str, Any]


class TronAQRecordsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    records: list[TronAQRecord] = []
    total: int
    page: int
    size: int
