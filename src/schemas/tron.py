from datetime import datetime
from typing import Annotated, Any

from base58 import b58decode
from pydantic import BaseModel, ConfigDict, Field, conint, field_validator


class TronAddressQueryRequest(BaseModel):
    address: str

    @field_validator("address")
    @classmethod
    def validate_address(cls, value):
        try:
            decoded = b58decode(value)
            if len(decoded) != 21 or decoded[0] != 0x41:
                raise ValueError("Invalid TRON address format")
            return value
        except Exception as e:
            raise ValueError(f"Invalid TRON address: {str(e)}")


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
