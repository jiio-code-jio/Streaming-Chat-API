from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.core.groq_client import get_client

router = APIRouter()

def generate_stream(prompt: str):
    client = get_client()
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        stream=True,
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield f"data: {content}\n\n"  # 🔥 THIS is streaming

@router.get("/chat/stream")
def stream_chat(prompt: str):
    return StreamingResponse(
        generate_stream(prompt),
        media_type="text/event-stream"
    )