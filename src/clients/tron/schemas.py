from pydantic import BaseModel, Field


class AccountModel(BaseModel):
    balance: int = Field(default=0, description="TRX balance in sun")


class AccountResourcesModel(BaseModel):
    freeNetUsed: int = Field(default=0, description="Used free bandwidth")
    freeNetLimit: int = Field(
        default=0, description="Total free bandwidth limit"
    )
    EnergyUsed: int | None = Field(default=0, description="Used energy")
    EnergyLimit: int | None = Field(
        default=0, description="Total energy limit"
    )


class AccountInfoModel(BaseModel):
    address: str = Field(description="TRON address")
    bandwidth_used: int = Field(description="Used bandwidth")
    bandwidth_limit: int = Field(description="Total bandwidth limit")
    energy_used: int = Field(description="Used energy")
    energy_limit: int = Field(description="Total energy limit")
    trx_balance: float = Field(description="TRX balance in TRX")
