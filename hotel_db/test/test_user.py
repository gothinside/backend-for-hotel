
import pytest
from conftest import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_create_user(client):
    user = {
        "email": "user@example.com",
        "password_hash": "secret"
    }
    res = await client.post(
        "/users/",
        json=user
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_not_unique_user(client):
    user = {
        "email": "user@example.com",
        "password_hash": "dqdqxsa",
        "is_active": False
    }
    res = await client.post(
        "/users/",
        json=user
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_update_user(client, create_new_user_id_101):
    user = {
        "email": create_new_user_id_101,
        "password_hash": "secret12"
    }
    res = await client.patch(
        f"/users/101",
        json=user,
        headers=create_test_auth_headers_for_user(create_new_user_id_101)
    )
    assert res.status_code == 200
    data = res.json()


@pytest.mark.asyncio
async def test_update2_user(client, create_new_user_id_101):
    user = {
        "email": "10000@example.com",
        "password_hash": "secret12"
    }
    res = await client.patch(
        f"/users/101",
        json=user,
        headers=create_test_auth_headers_for_user(create_new_user_id_101)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "10000@example.com"


@pytest.mark.asyncio
async def test_update_existing_user(client, create_new_user_id_101):
    user = {
        "email": "user@example.com",
        "password_hash": "secret"
    }
    res = await client.patch(
        f"/users/101",
        json=user,
        headers=create_test_auth_headers_for_user(create_new_user_id_101)
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_get_user(client, create_new_user_id_102):
    res = await client.get(
        f"/users/102",
        headers=create_test_auth_headers_for_user(create_new_user_id_102)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "2@example.com"
    assert data["is_active"] == True


@pytest.mark.asyncio
async def test_delete_user(client, create_new_user_id_102):
    res = await client.delete(
        f"/users/102",
        headers=create_test_auth_headers_for_user(create_new_user_id_102)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "User was deleted"
