import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import APIError

from app.config import settings
from app.retrieval import Retriever
from app.llm import LLMClient
from app.cache import AnswerCache


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Load components when application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.retriever = Retriever(
        model_name=settings.EMBEDDING_MODEL
    )

    app.state.llm_client = LLMClient()
    app.state.cache = AnswerCache(max_size=100)

    yield

    await app.state.llm_client.close()


app = FastAPI(
    title="Regulation Q&A API",
    description="Ask questions about regulatory PDF documents.",
    version="1.0.0",
    lifespan=lifespan
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "project": "Regulation Q&A API"
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # Normalize question for consistent cache keys
    cache_key = question.lower()

    # Check cache first
    cached_result = app.state.cache.get(cache_key)

    if cached_result is not None:
        logger.info("Cache HIT for question: %s", question)

        return {
            **cached_result,
            "cache": "HIT"
        }

    logger.info("Cache MISS for question: %s", question)

    total_start = time.perf_counter()

    try:
        # Retrieval
        retrieval_start = time.perf_counter()

        results = await asyncio.to_thread(
            app.state.retriever.search,
            question,
            settings.TOP_K
        )

        retrieval_time = time.perf_counter() - retrieval_start

        logger.info(
            "Retrieval completed in %.4f seconds",
            retrieval_time
        )

        if not results:
            response_data = {
                "question": question,
                "answer": "I couldn't find this in the provided documents",
                "sources": []
            }

            app.state.cache.set(cache_key, response_data)

            return {
                **response_data,
                "cache": "MISS"
            }

        # Prepare context and sources
        context_parts = []
        sources = []

        for number, result in enumerate(results, start=1):

            context_parts.append(
                f"[Source {number}]\n"
                f"Document: {result['document']}\n"
                f"Page: {result['page']}\n"
                f"Content: {result['text']}"
            )

            sources.append({
                "source": number,
                "document": result["document"],
                "page": result["page"],
                "similarity": round(result["score"], 4)
            })

        context = "\n\n".join(context_parts)

        # LLM generation
        llm_start = time.perf_counter()

        answer = await app.state.llm_client.generate_answer(
            question,
            context
        )

        llm_time = time.perf_counter() - llm_start

        logger.info(
            "LLM generation completed in %.4f seconds",
            llm_time
        )

        response_data = {
            "question": question,
            "answer": answer,
            "sources": sources
        }

        # Store response in cache
        app.state.cache.set(cache_key, response_data)

        total_time = time.perf_counter() - total_start

        logger.info(
            "Total request time: %.4f seconds",
            total_time
        )

        return {
            **response_data,
            "cache": "MISS"
        }

    except APIError as error:
        logger.exception("LLM service error")

        raise HTTPException(
            status_code=502,
            detail=f"LLM service error: {str(error)}"
        )

    except Exception as error:
        logger.exception("Unexpected error")

        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(error)}"
        )