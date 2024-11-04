
import pytest
from conftest import create_test_auth_headers_for_user

@pytest.mark.asyncio
async def test_create_service(client, create_new_admin_id_100):
    service = {
        "service_name": "Test_service",
        "service_price": 0,
        "is_active": False
    }

    res = await client.post(
        "/services/",
        json = service,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )

    assert res.status_code == 200
    

@pytest.mark.asyncio
async def test_create_existing_service(client, create_new_admin_id_100):
    service = {
        "service_name": "Test_service",
        "service_price": 500,
        "is_active": True
    }

    res = await client.post(
        "/services/",
        json = service,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )

    assert res.status_code == 400

@pytest.mark.asyncio
async def test_update_service(client, create_new_admin_id_100, create_service_id_100):
    service = {
        "service_name": "Test_update",
        "service_price": 30,
        "is_active": False
    }

    res = await client.patch(
        "/services/100",
        json = service,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )

    assert res.status_code == 200
    data = res.json()
    assert data["service_name"] == "Test_update"
    assert data["service_price"] == 30
    assert data["is_active"] == False

@pytest.mark.asyncio
async def test_update_fake_service(client, create_new_admin_id_100, create_service_id_100):
    service = {
        "service_name": "Test_update",
        "service_price": 30,
        "is_active": False
    }

    res = await client.patch(
        "/services/99",
        json = service,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )

    assert res.status_code == 404

@pytest.mark.asyncio
async def test_update_existing_service(client, create_new_admin_id_100, create_service_id_100):
    service = {
        "service_name": "Test_service",
        "service_price": 30,
        "is_active": False
    }

    res = await client.patch(
        "/services/100",
        json = service,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_delete_service(client, create_new_admin_id_100, create_service_id_100):
    res = await client.delete(
        "/services/100",
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200