import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.database import db, get_database
from app.config import get_settings

settings = get_settings()

TEST_DATABASE_NAME = "test_monolithic_app_db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    client = AsyncIOMotorClient(settings.mongodb_url)
    test_database = client[TEST_DATABASE_NAME]
    
    await test_database.users.create_index("email", unique=True)
    
    db.client = client
    db.db = test_database
    
    yield test_database
    
    await client.drop_database(TEST_DATABASE_NAME)
    client.close()


@pytest.fixture
async def clean_db(test_db):
    await test_db.users.delete_many({})
    yield test_db


@pytest.fixture
async def client(clean_db) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_database] = lambda: clean_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def valid_user_data():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }


@pytest.fixture
async def registered_user(client: AsyncClient, valid_user_data):
    response = await client.post("/api/auth/register", json=valid_user_data)
    assert response.status_code == 201
    return {**valid_user_data, **response.json()}


@pytest.fixture
async def auth_token(client: AsyncClient, registered_user):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]
