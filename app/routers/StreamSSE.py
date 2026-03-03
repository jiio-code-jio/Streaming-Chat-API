from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.core.groq_client import get_client
from app.core.memory import conversation_history  # shared history

router = APIRouter()


def generate_stream(prompt: str):
    client = get_client()

    # Step 1: append user message to shared history BEFORE calling the LLM
    conversation_history.append({
        "role": "user",
        "content": prompt
    })

    stream = client.chat.completions.create(
        messages=conversation_history,   # full history, not just current prompt
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        stream=True,
    )

    # Step 2: collect full response while streaming tokens to the client
    full_response = ""

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content
            yield f"data: {content}\n\n"   # stream each token via SSE

    # Step 3: once stream ends, save assistant reply to history
    conversation_history.append({
        "role": "assistant",
        "content": full_response
    })


@router.get("/chat/stream")
def stream_chat(prompt: str):
    return StreamingResponse(
        generate_stream(prompt),
        media_type="text/event-stream"
    )