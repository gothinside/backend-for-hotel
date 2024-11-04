
import pytest
from conftest import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_create_user(client, create_new_admin_id_100):
    category = {
        "category_name": "std",
        "price": 2000,
        "beds": 1
    }

    res = await client.post(
        "/categories/",
        json=category,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["category_name"] == "std"
    assert data["price"] == 2000
    assert data["beds"] == 1
    assert data["tables"] == 1
    assert data["is_wifi"] == True
    assert data["is_tv"] == True


@pytest.mark.asyncio
async def test_create_existing_category(client, create_new_admin_id_100):
    category = {
        "category_name": "std",
        "price": 2110,
        "beds": 5
    }

    res = await client.post(
        "/categories/",
        json=category,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_update_category(client, create_new_admin_id_100, create_new_category_id_100):
    category = {
        "category_name": "std2",
        "price": 4000,
        "beds": 2
    }

    res = await client.patch(
        "/categories/100",
        json=category,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["category_name"] == "std2"
    assert data["price"] == 4000
    assert data["beds"] == 2

@pytest.mark.asyncio
async def test_update_fake_category(client, create_new_admin_id_100, create_new_category_id_100):
    category = {
        "category_name": "std2",
        "price": 4000,
        "beds": 2
    }

    res = await client.patch(
        "/categories/99",
        json=category,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_existing_category(client, create_new_admin_id_100, create_new_category_id_100):
    category = {
        "category_name": "std",
        "price": 2000,
        "beds": 1,
        "is_wifi": False
    }

    res = await client.patch(
        "/categories/100",
        json=category,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_update_emprt_category(client, create_new_admin_id_100, create_new_category_id_100):
    category = {

    }

    res = await client.patch(
        "/categories/100",
        json=category,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400

@pytest.mark.asyncio
async def delete_category(client, create_new_admin_id_100, create_new_category_id_100):
    res = await client.patch(
        "/categories/100",
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    assert res.json()["message"] == "Category deleted"
