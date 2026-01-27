import pytest
from httpx import AsyncClient


class TestRegistration:
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, valid_user_data):
        response = await client.post("/api/auth/register", json=valid_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == valid_user_data["name"]
        assert data["email"] == valid_user_data["email"]
        assert "_id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, registered_user, valid_user_data):
        response = await client.post("/api/auth/register", json=valid_user_data)
        
        assert response.status_code == 409
        assert "already" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_weak_password_no_uppercase(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepass123!"
        })
        
        assert response.status_code == 422
        assert "uppercase" in str(response.json()).lower()

    @pytest.mark.asyncio
    async def test_register_weak_password_no_number(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "SecurePass!"
        })
        
        assert response.status_code == 422
        assert "digit" in str(response.json()).lower()

    @pytest.mark.asyncio
    async def test_register_weak_password_no_special(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "SecurePass123"
        })
        
        assert response.status_code == 422
        assert "special" in str(response.json()).lower()

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Short1!"
        })
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_name(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "name": "A",
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={})
        
        assert response.status_code == 422


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, registered_user):
        response = await client.post("/api/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, registered_user):
        response = await client.post("/api/auth/login", json={
            "email": registered_user["email"],
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={
            "email": "invalid-email",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 422


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient, registered_user, auth_token):
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == registered_user["name"]
        assert data["email"] == registered_user["email"]
        assert "_id" in data
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client: AsyncClient):
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_malformed_auth_header(self, client: AsyncClient):
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "InvalidFormat token"}
        )
        
        assert response.status_code == 403


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
