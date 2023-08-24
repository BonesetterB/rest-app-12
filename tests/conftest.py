from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.database.db import Base,get_db
from main import app
import pytest
import asyncio
import aiosqlite
from src.database.model import User
from src.services.auth import auth_service



SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.sqlite"


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

@pytest.fixture(scope='module')
def user():
    return {'username':"Corvin", 'email':"example@example.com", 'password':'123456BCD'}


@pytest.fixture(scope='module',autouse=True)
def init_models_fixture(user):

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash=auth_service.get_password_hash(user.get('password'))
            current_user= User(username=user.get('username'),email=user.get('email'),password=hash,confirmed=True)
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())

@pytest.fixture(scope='module')
def client():
    
    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

@pytest.fixture(scope='module')
def get_token(client,user):
    response = client.post("/auth/login",data={'username':user.get('email'), 'password':user.get('password')})

    assert  response.status_code == 200, response.text
    data= response.json()
    return data["access_token"]