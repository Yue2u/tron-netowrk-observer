import uuid

from base58 import b58decode
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from .base import Base
from .mixins import TimestampedMixin


class TronAddressQuery(Base, TimestampedMixin):
    id: Mapped[uuid.UUID] = mapped_column(
        default_factory=uuid.uuid4, primary_key=True
    )
    address: Mapped[str] = mapped_column(String(34), nullable=False)
    address_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=None
    )

    @validates("address")
    def validate_address(self, _, address):
        try:
            if len(address) != 34:
                raise ValueError("TRON address must be 34 characters long")
            decoded = b58decode(address)
            if len(decoded) != 21 or decoded[0] != 0x41:
                raise ValueError("Invalid TRON address format")
            return address
        except Exception as e:
            raise ValueError(f"Invalid TRON address: {str(e)}")
