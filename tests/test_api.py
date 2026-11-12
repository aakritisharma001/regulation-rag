from contextlib import asynccontextmanager

from fastapi.testclient import TestClient

from app.main import app
from app.cache import AnswerCache


class FakeRetriever:
    def search(self, query, top_k=3):
        return [
            {
                "document": "sample_rbi.pdf",
                "page": 1,
                "text": "The Reserve Bank of India is India's central bank.",
                "score": 0.85
            }
        ]


class FakeLLMClient:
    async def generate_answer(self, question, context):
        return "The RBI is India's central bank. [Source 1]"

    async def close(self):
        pass


@asynccontextmanager
async def custom_test_lifespan(application):
    application.state.retriever = FakeRetriever()
    application.state.llm_client = FakeLLMClient()
    application.state.cache = AnswerCache(max_size=100)

    yield


# Replace the real startup process during testing
app.router.lifespan_context = custom_test_lifespan


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_ask_endpoint():
    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={"question": "What is RBI?"}
        )

        data = response.json()

        assert response.status_code == 200
        assert "central bank" in data["answer"]
        assert len(data["sources"]) == 1
        assert data["sources"][0]["document"] == "sample_rbi.pdf"
        assert data["cache"] == "MISS"


def test_ask_endpoint_uses_cache():
    with TestClient(app) as client:
        first_response = client.post(
            "/ask",
            json={"question": "What is RBI?"}
        )

        second_response = client.post(
            "/ask",
            json={"question": "What is RBI?"}
        )

        assert first_response.json()["cache"] == "MISS"
        assert second_response.json()["cache"] == "HIT"

        assert (
            first_response.json()["answer"]
            == second_response.json()["answer"]
        )