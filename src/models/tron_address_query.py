import uuid

from base58 import b58decode_check
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from .base import Base
from .mixins import TimestampedMixin


class TronAddressQuery(Base, TimestampedMixin):
    __tablename__ = "tron_address_query"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    address: Mapped[str] = mapped_column(String(34), nullable=False)
    address_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=None
    )

    @validates("address")
    def validate_address(self, _, address):
        if not isinstance(address, str):
            raise ValueError("Address must be a string")

        # Базовые проверки
        if len(address) != 34:
            raise ValueError("Address must be 34 characters long")

        if not address.startswith("T"):
            raise ValueError("Address must start with 'T'")

        # Проверка символов (Base58)
        BASE58_ALPHABET = (
            "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        )
        for char in address:
            if char not in BASE58_ALPHABET:
                raise ValueError(f"Invalid character '{char}' in address")

        try:
            decoded = b58decode_check(address)
            # Декодированный адрес (без checksum) должен быть 21 байт (1 байт версии + 20 байт публичного ключа)
            if len(decoded) != 21:
                raise ValueError(
                    "Invalid address length after Base58 decoding"
                )

        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid address format: {str(e)}")

        return address
