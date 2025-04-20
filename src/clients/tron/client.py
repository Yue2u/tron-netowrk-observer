import asyncio
from typing import Any

import httpx
from base58 import b58decode

from .exceptions import TronClientException
from .schemas import AccountInfoModel, AccountModel, AccountResourcesModel


class TronClient:
    _client: httpx.AsyncClient

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str = "https://api.shasta.trongrid.io",
    ) -> None:
        self._client = client
        self._base_url = base_url

    async def get_account(self, address: str) -> AccountModel:
        """Get account info (including TRX)."""
        response = await self._client.post(
            f"{self._base_url}/wallet/getaccount",
            json={"address": address, "visible": True},
        )
        response.raise_for_status()
        return AccountModel.model_validate(response.json())

    async def get_account_resources(
        self, address: str
    ) -> AccountResourcesModel:
        """Get bandwith and energy info."""
        url = f"{self._base_url}/wallet/getaccountresource"
        payload = {"address": address, "visible": True}
        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        return AccountResourcesModel.model_validate(response.json())

    def validate_address(self, address: str) -> bool:
        """Check TRON address is valid."""
        try:
            decoded = b58decode(address)
            return len(decoded) == 21 and decoded[0] == 0x41
        except Exception:
            return False

    async def get_account_info(self, address: str) -> AccountInfoModel:
        """Get bandwidth, energy and TRX balance by address."""
        if not self.validate_address(address):
            raise TronClientException(400, "Invalid TRON address")

        try:
            account, resources = await asyncio.gather(
                self.get_account(address), self.get_account_resources(address)
            )

            return AccountInfoModel(
                address=address,
                bandwidth_used=resources.freeNetUsed,
                bandwidth_limit=resources.freeNetLimit,
                energy_used=resources.EnergyUsed,
                energy_limit=resources.EnergyLimit,
                trx_balance=account.balance
                / 1_000_000,  # Convert from sun to TRX
            )
        except httpx.HTTPStatusError as e:
            raise TronClientException(
                e.response.status_code, f"HTTP error: {e.response.text}"
            )
        except Exception as e:
            raise TronClientException(
                400, f"Error fetching account info: {str(e)}"
            )
