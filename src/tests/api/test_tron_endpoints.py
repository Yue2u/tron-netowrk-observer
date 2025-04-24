import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from pydantic import ValidationError

from routers.tron import router
from clients.tron import TronClient, TronClientException, get_tron_client
from cruds.uow import UoW, get_uow
from models.tron_address_query import TronAddressQuery
from schemas.tron import (
    TronAddressQueryRequest,
    TronAddressQueryResponse,
    TronAQRecordsRequest,
    TronAQRecordsResponse,
)

# Unit Tests

@pytest.mark.asyncio
async def test_get_account_info_success():
    # Setup
    mock_tron_client = AsyncMock(spec=TronClient)
    mock_tron_aq = AsyncMock()
    mock_uow = AsyncMock(spec=UoW, spec_set=['tron_aq'])
    mock_uow.tron_aq = mock_tron_aq
    
    test_address = "TNMcQVGPzqH9ZfMCSY4PNrukevtDgp24dK"
    mock_response = TronAddressQueryResponse(
        address=test_address,
        bandwidth_used=100,
        bandwidth_limit=5000,
        energy_used=200,
        energy_limit=1000,
        trx_balance=100.5
    )
    
    # Настраиваем мок для метода get_account_info
    async def mock_get_account_info(address):
        print(f"Received address in mock: {address}")  # Отладочная информация
        if address != test_address:
            raise AssertionError(f"Expected address {test_address}, got {address}")
        return mock_response
    
    mock_tron_client.get_account_info = mock_get_account_info
    
    # Test
    from routers.tron import get_account_info
    response = await get_account_info(
        tron_client=mock_tron_client,
        uow=mock_uow,
        req=TronAddressQueryRequest(address=test_address)
    )
    
    # Assert
    assert response.address == test_address
    assert response.bandwidth_used == 100
    assert response.bandwidth_limit == 5000
    assert response.energy_used == 200
    assert response.energy_limit == 1000
    assert response.trx_balance == 100.5
    mock_tron_aq.insert_record.assert_called_once()

@pytest.mark.asyncio
async def test_get_account_info_error():
    # Setup
    mock_tron_client = AsyncMock(spec=TronClient)
    mock_tron_aq = AsyncMock()
    mock_uow = AsyncMock(spec=UoW, spec_set=['tron_aq'])
    mock_uow.tron_aq = mock_tron_aq
    
    test_address = "TRfffNywtDL6wEamxg8V46LJfyR8Fvy7nu"  # Валидный адрес TRON
    
    # Настраиваем мок для метода get_account_info
    async def mock_get_account_info(address):
        print(f"Received address in mock: {address}")  # Отладочная информация
        raise TronClientException(
            status_code=400,
            detail="Invalid address format"
        )
    
    mock_tron_client.get_account_info = mock_get_account_info
    
    # Test and Assert
    from routers.tron import get_account_info
    with pytest.raises(HTTPException) as exc_info:
        await get_account_info(
            tron_client=mock_tron_client,
            uow=mock_uow,
            req=TronAddressQueryRequest(address=test_address)
        )
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid address format"

@pytest.mark.asyncio
async def test_get_account_info_validation_error():
    # Setup
    invalid_address = "invalid_address"
    
    # Test and Assert
    with pytest.raises(ValidationError):
        TronAddressQueryRequest(address=invalid_address)

@pytest.mark.asyncio
async def test_get_records_info_success():
    # Setup
    mock_tron_aq = AsyncMock()
    mock_uow = AsyncMock(spec=UoW, spec_set=['tron_aq'])
    mock_uow.tron_aq = mock_tron_aq
    
    mock_response = {
        "records": [],
        "total": 0,
        "page": 1,
        "size": 10
    }
    mock_tron_aq.get_paginated.return_value = mock_response
    
    # Test
    from routers.tron import get_records_info
    response = await get_records_info(
        uow=mock_uow,
        page_size=10,
        page_number=1
    )
    
    # Assert
    assert response == mock_response
    mock_tron_aq.get_paginated.assert_called_once_with(
        page_size=10,
        page_number=1
    )

# Integration Tests

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def mock_tron_client():
    mock = AsyncMock(spec=TronClient)
    
    # Настраиваем мок для метода get_account_info
    async def mock_get_account_info(address):
        print(f"Received address in mock fixture: {address}")  # Отладочная информация
        return TronAddressQueryResponse(
            address=address,
            bandwidth_used=100,
            bandwidth_limit=5000,
            energy_used=200,
            energy_limit=1000,
            trx_balance=100.5
        )
    
    mock.get_account_info = mock_get_account_info
    return mock

@pytest.fixture
def mock_tron_aq():
    return AsyncMock()

@pytest.fixture
def mock_uow(mock_tron_aq):
    mock = AsyncMock(spec=UoW, spec_set=['tron_aq'])
    mock.tron_aq = mock_tron_aq
    return mock

@pytest.mark.asyncio
async def test_integration_get_account_info(client, mock_tron_client, mock_uow, mock_tron_aq):
    # Setup
    test_address = "TRfffNywtDL6wEamxg8V46LJfyR8Fvy7nu"  # Валидный адрес TRON
    
    # Override dependencies
    client.app.dependency_overrides[get_tron_client] = lambda: mock_tron_client
    client.app.dependency_overrides[get_uow] = lambda: mock_uow
    
    # Test
    response = client.post(
        "/tron/account_info",
        json={"address": test_address}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == test_address
    assert data["bandwidth_used"] == 100
    assert data["bandwidth_limit"] == 5000
    assert data["energy_used"] == 200
    assert data["energy_limit"] == 1000
    assert data["trx_balance"] == 100.5

@pytest.mark.asyncio
async def test_integration_get_account_info_validation_error(client, mock_tron_client, mock_uow):
    # Setup
    invalid_address = "invalid_address"
    
    # Override dependencies
    client.app.dependency_overrides[get_tron_client] = lambda: mock_tron_client
    client.app.dependency_overrides[get_uow] = lambda: mock_uow
    
    # Test
    response = client.post(
        "/tron/account_info",
        json={"address": invalid_address}
    )
    
    # Assert
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_integration_get_records_info(client, mock_uow, mock_tron_aq):
    # Setup
    mock_response = {
        "records": [],
        "total": 0,
        "page": 1,
        "size": 10
    }
    mock_tron_aq.get_paginated.return_value = mock_response
    
    # Override dependency
    client.app.dependency_overrides[get_uow] = lambda: mock_uow
    
    # Test
    response = client.get(
        "/tron/records_info",
        params={"page_size": 10, "page_number": 1}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    import logging
    logging.warning(f"{data}")
    assert data == mock_response 