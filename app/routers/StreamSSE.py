# app/routers/StreamSSE.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json                                        # ← NEW
from app.core.groq_client import get_client
from app.core.memory import conversation_history

router = APIRouter()


def generate_stream(prompt: str):
    client = get_client()

    conversation_history.append({"role": "user", "content": prompt})

    stream = client.chat.completions.create(
        messages=conversation_history,
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        stream=True,
    )

    full_response = ""

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content
            # json.dumps encodes ALL special chars — newlines, quotes, backslashes
            # Frontend uses JSON.parse() to restore the original token perfectly
            yield f"data: {json.dumps(content)}\n\n"   # ← CHANGED

    conversation_history.append({"role": "assistant", "content": full_response})


@router.get("/chat/stream")
def stream_chat(prompt: str):
    return StreamingResponse(
        generate_stream(prompt),
        media_type="text/event-stream"
    )