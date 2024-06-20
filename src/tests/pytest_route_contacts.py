from unittest.mock import patch
import pytest

from src.services.auth import auth_service


@pytest.fixture
def get_token():
    return "test_token"


def test_create_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "phone_number": "1234567890"
        }
        response = client.post("/contacts/", headers=headers, json=contact_data)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "johndoe@example.com"
        assert data["phone_number"] == "1234567890"


def test_read_contacts(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/contacts/", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)


def test_read_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_id = 1
        response = client.get(f"/contacts/{contact_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["id"] == contact_id
        else:
            assert response.status_code == 404


def test_update_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_id = 1
        update_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe@example.com",
            "phone_number": "0987654321"
        }
        response = client.put(f"/contacts/{contact_id}", headers=headers, json=update_data)
        if response.status_code == 200:
            data = response.json()
            assert data["first_name"] == "Jane"
            assert data["last_name"] == "Doe"
            assert data["email"] == "janedoe@example.com"
            assert data["phone_number"] == "0987654321"
        else:
            assert response.status_code == 404


def test_delete_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_id = 1
        response = client.delete(f"/contacts/{contact_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == contact_id
        else:
            assert response.status_code == 404
