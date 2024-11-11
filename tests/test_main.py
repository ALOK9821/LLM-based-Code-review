import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_analyze_pr_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/analyze-pr", json={
            "repo_url": "https://github.com/pandas-dev/pandas",
            "pr_number": "60266"
        })
    assert response.status_code == 200
    assert "task_id" in response.json()

@pytest.mark.asyncio
async def test_status_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/status/851d3695-c715-45c7-ac72-bfda8b4e86b7")
    assert response.status_code == 200
    assert "status" in response.json()

@pytest.mark.asyncio
async def test_results_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/results/851d3695-c715-45c7-ac72-bfda8b4e86b7")
    assert response.status_code == 200
    assert "status" in response.json()
