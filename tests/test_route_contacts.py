import pytest
from unittest.mock import  MagicMock, patch, AsyncMock
from src.services.auth import auth_service


def test_get_contacts_(client, get_token, monkeypatch):
    with patch.object(auth_service, attribute='cache') as redis_mok:
        redis_mok.get.return_value= None
        response = client.get("/main/contacts",headers={'Authorization':f"Bearer {get_token}"})
        assert response.status_code == 200, response.text
        data =response.json()
        assert type(data) == list



def test_get_contact_(client, get_token, monkeypatch):
    with patch.object(auth_service, attribute='cache') as redis_mok:
        redis_mok.get.return_value= None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("/main/contacts/1",headers={'Authorization':f"Bearer {get_token}"})
        assert response.status_code == 404, response.text
        data =response.json()
        assert "detail" in data

def test_created_contact_(client, get_token):
    with patch.object(auth_service, attribute='cache') as redis_mok:
        redis_mok.get.return_value= None
        response = client.post("/main/contact/",headers={'Authorization':f"Bearer {get_token}"}, json={"name":"Juniver",
                                                                                                        "surname":"Wulfsai",
                                                                                                        "email":"usebvfr@example.com",
                                                                                                        "phone":"896972",
                                                                                                        "birthday":"2023-08-24",
                                                                                                        "notes":"YdsEes",})
        assert response.status_code == 201, response.text
        data =response.json()
        assert "detail" in data
        assert data["detail"]=='created were Successful'


def test_update_contacts_(client, get_token, monkeypatch):
    with patch.object(auth_service, attribute='cache') as redis_mok:
        redis_mok.get.return_value= None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.put("/main/contact/1",headers={'Authorization':f"Bearer {get_token}"}, json={"name":"Miv",
                                                                                                        "surname":"Marlon",
                                                                                                        "email":"uMikaso@example.com",
                                                                                                        "phone":"8666972",
                                                                                                        "birthday":"2023-08-30",
                                                                                                        "notes":"None",})
        assert response.status_code == 200, response.text
        data =response.json()
        assert data["name"] == "Miv"

def test_search_contacts_(client, get_token, monkeypatch):
    with patch.object(auth_service, attribute='cache') as redis_mok:
        redis_mok.get.return_value= None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("/main/contact/Miv",headers={'Authorization':f"Bearer {get_token}"})
        assert response.status_code == 200, response.text
        data =response.json()
        assert isinstance(data, list)
        assert len(data) > 0

def test_hbp_contacts_(client, get_token, monkeypatch):
    with patch.object(auth_service, attribute='cache') as redis_mok:
        redis_mok.get.return_value= None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("/main/contacts/HB",headers={'Authorization':f"Bearer {get_token}"})
        assert response.status_code == 200, response.text
        data =response.json()
        assert isinstance(data, list)
        assert len(data) > 0


def test_delete_contacts_(client, get_token, monkeypatch):
    with patch.object(auth_service, attribute='cache') as redis_mok:
        redis_mok.get.return_value= None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.delete("/main/contact/1",headers={'Authorization':f"Bearer {get_token}"})
        assert response.status_code == 200, response.text
        data =response.json()
        assert data == {"message": "Contact deleted successfully"}







        