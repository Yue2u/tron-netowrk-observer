from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from clients.tron import TronClient, TronClientException, get_tron_client
from cruds.uow import UoW, get_uow
from models.tron_address_query import TronAddressQuery
from schemas.tron import (
    TronAddressQueryRequest,
    TronAddressQueryResponse,
    TronAQRecordsRequest,
    TronAQRecordsResponse,
)

router = APIRouter(prefix="/tron", tags=["tron"])


@router.post("/account_info", response_model=TronAddressQueryResponse)
async def get_account_info(
    tron_client: Annotated[TronClient, Depends(get_tron_client)],
    uow: Annotated[UoW, Depends(get_uow)],
    req: TronAddressQueryRequest,
):
    try:
        resp_data = await tron_client.get_account_info(req.address)
    except TronClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    await uow.tron_aq.insert_record(
        address=resp_data.address,
        address_data=resp_data.model_dump(
            exclude=set(["address"]), exclude_unset=True
        ),
    )
    return TronAddressQueryResponse(**resp_data.model_dump())


@router.get("/records_info")
async def get_recoreds_info(
    uow: Annotated[UoW, Depends(get_uow)], req: TronAQRecordsRequest
):
    return await uow.tron_aq.get_paginated(
        page_size=req.page_size, page_number=req.page_number
    )
