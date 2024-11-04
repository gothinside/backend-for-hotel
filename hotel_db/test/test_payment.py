
import pytest
from conftest import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_get_payment(client, create_new_admin_id_100, create_new_payment_id_100):
    res = await client.get(
        "/payments/100",
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["amount"] == 6000
    assert data["payment_date"] == "2024-08-10T00:00:00"


@pytest.mark.asyncio
async def test_update_payment(client, create_new_admin_id_100, create_new_payment_id_100):
    patch_data = {
        "amount": 10000
    }
    res = await client.patch(
        "/payments/100",
        json=patch_data,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["amount"] == 10000
    assert data["payment_date"] == "2024-08-10T00:00:00"


@pytest.mark.asyncio
async def test_get_payment(client, create_new_admin_id_100, create_new_payment_id_100):
    res = await client.delete(
        "/payments/100",
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
