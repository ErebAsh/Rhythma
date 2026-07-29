import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth import get_current_user
from services.firestore_service import AssistantConversationService

logger = logging.getLogger(__name__)

# ─── Rate Limiter (in-memory, resets on restart) ──────────────────────────
_assistant_rate_history = {}

ASSISTANT_RATE_LIMIT = int(os.getenv("ASSISTANT_RATE_LIMIT", "10"))
ASSISTANT_RATE_WINDOW = int(os.getenv("ASSISTANT_RATE_WINDOW", "60"))


def is_rate_limited(user_id: str) -> Optional[int]:
    now = datetime.now(timezone.utc)
    if user_id in _assistant_rate_history:
        _assistant_rate_history[user_id] = [
            t for t in _assistant_rate_history[user_id]
            if now - t < timedelta(seconds=ASSISTANT_RATE_WINDOW)
        ]
    else:
        _assistant_rate_history[user_id] = []

    if len(_assistant_rate_history[user_id]) >= ASSISTANT_RATE_LIMIT:
        oldest = _assistant_rate_history[user_id][0]
        remaining = int((oldest + timedelta(seconds=ASSISTANT_RATE_WINDOW) - now).total_seconds())
        return max(remaining, 1)

    _assistant_rate_history[user_id].append(now)
    return None


class ChatMessage(BaseModel):
    role: str
    content: str


class AssistantRequest(BaseModel):
    message: str
    language: Optional[str] = "en"
    history: Optional[List[ChatMessage]] = None


class AssistantResponse(BaseModel):
    response: str
    language: str
    disclaimer: str = "Please consult a healthcare professional for medical advice."


SYSTEM_PROMPT = """
You are Rhythma, a compassionate and knowledgeable AI menstrual health companion designed specifically for women in India. Your purpose is to provide supportive, culturally sensitive, and medically responsible guidance on menstrual health, reproductive health, emotional well-being, and overall women's health.

Key guidelines:
- Always prioritize safety and remind users to consult a doctor for medical advice.
- Keep responses concise, empathetic, and easy to understand.
- Use simple English or the user's preferred Indian language.
- Be non-judgmental and encouraging.
- Do not provide medical diagnoses - encourage professional consultation.
- Never prescribe medication.
- If you don't know something, say so honestly.
- Always end responses that involve symptoms or health concerns with a gentle reminder to consult a healthcare professional.
"""

router = APIRouter(tags=["AI Assistant"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY is not set. Assistant requests will fail until it is configured.")
else:
    genai.configure(api_key=GEMINI_API_KEY)


@router.post("/chat", response_model=AssistantResponse)
async def chat(
    request: AssistantRequest,
    current_user: dict = Depends(get_current_user),
):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="AI service not configured.")

    user_id = current_user.get("id")

    # Rate limit check
    remaining = is_rate_limited(user_id)
    if remaining is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please wait {remaining} seconds before sending another message.",
            headers={"Retry-After": str(remaining)},
        )

    # Load persisted history from Firestore, falling back to client-provided history
    persisted = AssistantConversationService.get_recent_messages(user_id, limit=10)
    history = [ChatMessage(**m) if isinstance(m, dict) else m for m in persisted]

    if not history and request.history:
        history = request.history[-10:]

    prompt_parts = [
        f"System: {SYSTEM_PROMPT}",
        f"Language: Respond in {request.language}.",
        "\n--- Conversation History ---",
    ]

    if history:
        for msg in history[-10:]:
            if msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "model":
                prompt_parts.append(f"Assistant: {msg.content}")
    else:
        prompt_parts.append("(No previous messages)")

    prompt_parts.extend(
        [
            "\n--- Current Message ---",
            f"User: {request.message}",
            "Assistant:",
        ]
    )

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content("\n".join(prompt_parts))
        reply = response.text.strip() if response.text else "I'm sorry, I couldn't process that."
        
        # Persist exchange to Firestore
        AssistantConversationService.add_messages(user_id, [
            {"role": "user", "content": request.message},
            {"role": "model", "content": reply},
        ])

        return AssistantResponse(
            response=reply,
            language=request.language or "en",
            disclaimer="Please consult a healthcare professional for medical advice.",
        )
    except Exception as exc:
        logger.error("Gemini API error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="AI service error. Please try again later.")


@router.get("/languages")
async def supported_languages(current_user: dict = Depends(get_current_user)):
    return [
        {"code": "en", "name": "English"},
        {"code": "hi", "name": "Hindi"},
        {"code": "mr", "name": "Marathi"},
        {"code": "ta", "name": "Tamil"},
        {"code": "te", "name": "Telugu"},
        {"code": "kn", "name": "Kannada"},
        {"code": "ml", "name": "Malayalam"},
        {"code": "bn", "name": "Bengali"},
        {"code": "gu", "name": "Gujarati"},
    ]