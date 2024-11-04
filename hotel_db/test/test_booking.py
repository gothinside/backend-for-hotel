
import pytest
from conftest import create_test_auth_headers_for_user


@pytest.mark.asyncio
async def test_create_booking(client, create_new_admin_id_100, create_new_room_id_102):
    booking = {
        "booking_data": {
            "join_date": "2024-07-27T18:41:23.244Z",
            "out_date": "2024-08-27T18:41:23.244Z",
            "room_num": 102
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00",
            },
            {
                "first_name": "Name1",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-01"
            }
        ],
        "services_ids": []
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    data = res.json()
    assert data[0]["room_num"] == 102
    assert data[1] == [
        {
            "first_name": "Name",
            "last_name": "Lastname",
            'id': 1,
            "phone_number": "8-000-000-00-00",
        },
        {
            "first_name": "Name1",
            "last_name": "Lastname",
            'id': 2,
            "phone_number": "8-000-000-00-01"
        }
    ]

@pytest.mark.asyncio
async def test_create_booking_with_invalid_out_date(client, create_new_admin_id_100, create_new_room_id_102):
    booking = {
        "booking_data": {
            "join_date": "2024-04-27T18:41:23.244Z",
            "out_date": "2024-08-26T18:41:23.244Z",
            "room_num": 102
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00",
            },
            {
                "first_name": "Name1",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-01"
            }
        ],
        "services_ids": []
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_create_booking_with_invalid_join_date(client, create_new_admin_id_100, create_new_room_id_102):
    booking = {
        "booking_data": {
            "join_date": "2024-07-29T18:41:23.244Z",
            "out_date": "2024-10-27T18:41:23.244Z",
            "room_num": 102
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00",
            },
            {
                "first_name": "Name1",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-01"
            }
        ],
        "services_ids": []
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_create_booking_no_existing_room(client, create_new_admin_id_100, create_new_room_id_102):
    booking = {
        "booking_data": {
            "join_date": "2024-07-27T18:41:23.244Z",
            "out_date": "2024-08-27T18:41:23.244Z",
            "room_num": 3
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00"
            }
        ],
        "services_ids": []
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_create_booking_no_active_room(client, create_new_admin_id_100, create_new_room_id_103):
    booking = {
        "booking_data": {
            "join_date": "2024-07-27T18:41:23.244Z",
            "out_date": "2024-08-27T18:41:23.244Z",
            "room_num": 103
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00"
            }
        ],
        "services_ids": []
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_create_booking_with_service(client, create_new_admin_id_100, create_new_room_id_102, create_service_id_101):
    booking = {
        "booking_data": {
            "join_date": "2023-06-27T18:41:23.244Z",
            "out_date": "2023-08-27T18:41:23.244Z",
            "room_num": 102
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00"
            }
        ],
        "services_ids": [101]
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_create_booking_fake_service(client, create_new_admin_id_100, create_new_room_id_102, create_service_id_101):
    booking = {
        "booking_data": {
            "join_date": "2022-07-27T18:41:23.244Z",
            "out_date": "2022-08-27T18:41:23.244Z",
            "room_num": 102
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00"
            }
        ],
        "services_ids": [3]
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_create_booking_no_active_service(client, create_new_admin_id_100, create_new_room_id_102, create_service_id_102):
    booking = {
        "booking_data": {
            "join_date": "2024-07-27T18:41:23.244Z",
            "out_date": "2024-08-27T18:41:23.244Z",
            "room_num": 102
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00"
            }
        ],
        "services_ids": [102]
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_create_booking_with_too_many_clients(client, create_new_admin_id_100, create_new_room_id_102):
    booking = {
        "booking_data": {
            "join_date": "2024-07-27T18:41:23.244Z",
            "out_date": "2024-08-27T18:41:23.244Z",
            "room_num": 102
        },
        "clients": [
            {
                "first_name": "Name",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-00"
            },
            {
                "first_name": "Name1",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-01"
            },
            {
                "first_name": "Name2",
                "last_name": "Lastname",
                "phone_number": "8-000-000-00-02"
            }
        ],
        "services_ids": []
    }

    res = await client.post(
        "/bookings/",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_update_fake_booking(client, create_new_admin_id_100, create_new_room_id_104, create_service_id_101):
    booking = {
        "booking_data": {
            "join_date": "2024-07-27T18:41:23.244Z",
            "out_date": "2024-08-27T18:41:23.244Z",
            "room_num": 104
        },
        "clients": [
            {
                "first_name": "Name5",
                "last_name": "Lastname",
                "phone_number": "8-000-22-00-00"
            },
            {
                "first_name": "Name6",
                "last_name": "Lastname",
                "phone_number": "8-000-200-00-01"
            }
        ],
        "services_ids": [101]
    }

    res = await client.put(
        "/bookings/99",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_booking(client, create_new_admin_id_100, create_new_room_id_104, create_service_id_101):
    booking = {
        "booking_data": {
            "join_date": "2024-07-27T18:41:23.244Z",
            "out_date": "2024-08-27T18:41:23.244Z",
            "room_num": 104
        },
        "clients": [
            {
                "first_name": "Name5",
                "last_name": "Lastname",
                "phone_number": "8-000-22-00-00"
            },
            {
                "first_name": "Name6",
                "last_name": "Lastname",
                "phone_number": "8-000-200-00-01"
            }
        ],
        "services_ids": [101]
    }

    res = await client.put(
        "/bookings/1",
        json=booking,
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
    data = res.json()
    assert data[0]["room_num"] == 104
    assert data[1] == [
        {
            "first_name": "Name5",
            "last_name": "Lastname",
            'id': 3,
            "phone_number": "8-000-22-00-00",
        },
        {
            "first_name": "Name6",
            "last_name": "Lastname",
            'id': 4,
            "phone_number": "8-000-200-00-01"
        }
    ]
    assert data[2] == [101]


@pytest.mark.asyncio
async def test_update_booking(client, create_new_admin_id_100):

    res = await client.delete(
        "/bookings/1",
        headers=create_test_auth_headers_for_user(create_new_admin_id_100)
    )
    assert res.status_code == 200
