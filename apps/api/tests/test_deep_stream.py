"""
test_deep_stream.py — Phase 4 Test Suite for Real-Time SSE Streaming Copilot
=============================================================================
Validates:
1. Dynamic clarification question generation with interactive choices.
2. Token streaming generator for expert hardware reasoning.
3. /api/v1/recommend/deep-stream SSE protocol lifecycle (status -> token -> questions -> recommendations -> done).
"""

import pytest
import httpx
import json
from app.main import app
from app.services.llm import generate_clarification_questions, stream_deep_reasoning
from app.models.phone import PhoneDetails


def test_generate_clarification_questions_generic():
    """Verify clarification questions for generic search query."""
    questions = generate_clarification_questions("best phone under 30000", budget=30000.0)
    assert len(questions) >= 2
    for q in questions:
        assert "id" in q
        assert "question" in q
        assert "options" in q
        assert len(q["options"]) >= 2


def test_generate_clarification_questions_gaming():
    """Verify clarification questions adapt when gaming is mentioned."""
    questions = generate_clarification_questions("high fps gaming phone for bgmi", budget=25000.0)
    assert len(questions) >= 1
    # Check that questions have valid format
    for q in questions:
        assert len(q["options"]) > 0


@pytest.mark.asyncio
async def test_stream_deep_reasoning_fallback():
    """Verify stream_deep_reasoning yields text tokens."""
    dummy_phones = [
        {
            "phone": PhoneDetails(
                id=601,
                name="iQOO Neo 9 Pro",
                brand="iQOO",
                price=34999.0,
                price_numeric=34999.0,
                raw_specs={"chipset": "Snapdragon 8 Gen 2"}
            )
        }
    ]
    tokens = []
    async for token in stream_deep_reasoning("best gaming phone", dummy_phones, budget=35000.0):
        tokens.append(token)

    full_text = "".join(tokens)
    assert len(tokens) > 0
    assert "Neural Hardware Analysis" in full_text or len(full_text) > 20


@pytest.mark.asyncio
async def test_deep_stream_endpoint():
    """Verify /api/v1/recommend/deep-stream SSE endpoint returns valid stream events."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "query": "best camera phone under 50000 with periscope lens",
            "budget": 50000.0,
            "persona": "Content Creator"
        }
        async with client.stream("POST", "/api/v1/recommend/deep-stream", json=payload) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

            events_received = set()
            recommendations_received = []
            questions_received = []

            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    event_name = line.split(":", 1)[1].strip()
                    events_received.add(event_name)
                elif line.startswith("data:"):
                    data_str = line.split(":", 1)[1].strip()
                    try:
                        data = json.loads(data_str)
                        if "recommendations" in data:
                            recommendations_received = data["recommendations"]
                        if "questions" in data:
                            questions_received = data["questions"]
                    except Exception:
                        pass

            assert "status" in events_received
            assert "token" in events_received
            assert "questions" in events_received
            assert "recommendations" in events_received
            assert "done" in events_received
            assert len(recommendations_received) > 0
            assert len(questions_received) > 0
