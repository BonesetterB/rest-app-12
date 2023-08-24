import pytest
from unittest.mock import  MagicMock
from tests.conftest import TestingSessionLocal
from sqlalchemy import select
from src.database.model import User

user_mock = {"username":"Merlin",'email':"exefrmple@example.com", "password":"qwerty5"}

def test_create_user(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    response = client.post("/auth/signup",json=user_mock)
    assert  response.status_code == 201, response.text
    data= response.json()
    assert data.get('email') == user_mock.get('email')
    assert data.get('username') == user_mock.get('username')
    assert 'avatar' in data

def test_repeat_create_user(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    response = client.post("/auth/signup",json=user_mock)
    assert  response.status_code == 409, response.text
    data= response.json()
    assert data.get('detail') == "Account already exists"

def test_login_user_not(client, monkeypatch):
    response = client.post("/auth/login",data={'username':user_mock.get('email'), 'password':user_mock.get('password')})

    assert  response.status_code == 401, response.text
    data= response.json()
    assert data.get('detail') == "Email not confirmed"

@pytest.mark.asyncio
async def test_login_user(client, monkeypatch):
    async with TestingSessionLocal() as session: 
        curent_user= await session.execute(select(User).filter(User.email==user_mock.get('email')))
        curent_user=curent_user.scalar_one_or_none()
        curent_user.confirmed=True
        await session.commit()
    response = client.post("/auth/login",data={'username':user_mock.get('email'), 'password':user_mock.get('password')})

    assert  response.status_code == 200, response.text
    data= response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'token_type' in data


def test_login_password_user(client, monkeypatch):
    response = client.post("/auth/login",data={'username':user_mock.get('email'), 'password':'password'})

    assert  response.status_code == 401, response.text
    data= response.json()
    assert data.get('detail') == "Invalid password"


def test_login_email_user(client, monkeypatch):
    response = client.post("/auth/login",data={'username':'email', 'password':user_mock.get('password')})

    assert  response.status_code == 401, response.text
    data= response.json()
    assert data.get('detail') == "Invalid email"


def test_login_valid_user(client, monkeypatch):
    response = client.post("/auth/login",data={'username':'email'})

    assert  response.status_code == 422, response.text
    data= response.json()
    assert 'detail' in data
