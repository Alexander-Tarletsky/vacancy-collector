import pytest
from app.main import app
from httpx import AsyncClient


# pytestmark = pytest.mark.anyio



# @pytest.mark.asyncio
# async def test_create_item(async_client: AsyncClient, db_session: AsyncSession):
#     response = await async_client.post("/items/", json={"name": "Test Item",
#                                                         "description": "Test Description"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Test Item"
#
#     retrieved_item = await db_session.get(models.Item, data["id"])
#     assert retrieved_item
#     assert retrieved_item.name == "Test Item"


@pytest.mark.asyncio
async def test_get_user_channels(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/v1/channels")
    assert response.status_code == 200
    assert "data" in response.json()