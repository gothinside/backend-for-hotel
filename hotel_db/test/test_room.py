
import pytest
from conftest import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_create_room(client, create_new_admin_id_100, create_new_category_id_101):
    room = {
        "room_num": 1,
        "category_id": 101
    }
    res = await client.post(
        "/rooms/",
        json=room,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_create_existing_room(client, create_new_admin_id_100, create_new_category_id_101):
    room = {
        "room_num": 1,
        "category_id": 101
    }
    res = await client.post(
        "/rooms/",
        json=room,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_create_fake_category(client, create_new_admin_id_100, create_new_category_id_101):
    room = {
        "room_num": 2,
        "category_id": 102
    }
    res = await client.post(
        "/rooms/",
        json=room,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_room(client, create_new_admin_id_100, create_new_category_id_101):
    res = await client.get(
        "/rooms/1"
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_update_room(client, create_new_admin_id_100, create_new_room_id_100, create_new_category_id_102):
    room = {
        "room_num": 110,
        "category_id": 102
    }
    res = await client.patch(
        "/rooms/100",
        json=room,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["room_num"] == 110
    assert data["category_id"] == 102


@pytest.mark.asyncio
async def test_update_room_with_fake_category(client, create_new_admin_id_100, create_new_room_id_100, create_new_category_id_102):
    room = {
        "room_num": 111,
        "category_id": 3
    }
    res = await client.patch(
        "/rooms/100",
        json=room,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_fake_room(client, create_new_admin_id_100, create_new_room_id_100, create_new_category_id_102):
    room = {
        "room_num": 110,
        "category_id": 102
    }
    res = await client.patch(
        "/rooms/1000",
        json=room,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_update_existing_room(client, create_new_admin_id_100, create_new_room_id_101, create_new_category_id_102):
    room = {
        "room_num": 110,
        "category_id": 102
    }
    res = await client.patch(
        "/rooms/101",
        json=room,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400
    # data = res.json()
    # assert data["room_num"] == 110
    # assert data["category_id"] == 102


@pytest.mark.asyncio
async def test_delete_room(client, create_new_admin_id_100, create_new_room_id_101):
    res = await client.delete(
        "/rooms/101",
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    assert res.json()["message"] == "Room deleted"
