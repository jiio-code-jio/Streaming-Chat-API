# main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import time
import datetime
import logging
import httpx
from app.routers import StreamSSE
from app.core.groq_client import get_client
from app.core.memory import conversation_history  # ← imported from shared module
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq, GroqError

load_dotenv()

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def estimate_tokens(text: str) -> int:
    return len(text)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(StreamSSE.router)

client = get_client()

# conversation_history is no longer defined here — it lives in app/core/memory.py
# Both this file and StreamSSE.py import the SAME list object, so they share state.


class chatRequest(BaseModel):
    prompt: str

class chatResponse(BaseModel):
    output: str


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/chat")
def chat(request: chatRequest) -> chatResponse:
    max_retries = 3
    backoff_delays = [1, 2, 4]
    model_name = "llama-3.3-70b-versatile"

    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": request.prompt}],
                model=model_name
            )
            output_text  = chat_completion.choices[0].message.content
            total_tokens = estimate_tokens(request.prompt) + estimate_tokens(output_text)
            timestamp    = datetime.datetime.utcnow().isoformat()

            log_message = (
                f"Timestamp: {timestamp} | "
                f"Model: {model_name} | "
                f"Estimated Tokens: {total_tokens}"
            )
            print(log_message)
            logging.info(log_message)

            return chatResponse(output=output_text)

        except GroqError as e:
            status_code = getattr(e, "status_code", None)
            if status_code == 429 and attempt < max_retries - 1:
                time.sleep(backoff_delays[attempt])
                continue
            if status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
            raise HTTPException(status_code=400, detail=f"LLM API error: {str(e)}")

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")


@app.post("/chatHistory")
def chatHistory(request: chatRequest) -> chatResponse:
    conversation_history.append({"role": "user", "content": request.prompt})

    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="llama-3.3-70b-versatile"
    )
    assistant_reply = chat_completion.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_reply})

    return chatResponse(output=assistant_reply)


@app.delete("/chat/reset")
def delHistory():
    conversation_history.clear()
    conversation_history.append(
        {"role": "system", "content": "You are a helpful assistant and you give only answers."}
    )
    return {"History": "deleted"}


@app.get("/history")
def getHistory():
    return {"history": conversation_history}


@app.post("/chatMore")
async def chatMore(request: chatRequest):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": "return the response only in json inside messages also"},
        {"role": "user",   "content": request.prompt}
    ]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.7}
        )
    result = response.json()
    return {"reply": result["choices"][0]["message"]["content"]}


@app.get("/path")
async def pri():
    return {"message": "Hello World"}