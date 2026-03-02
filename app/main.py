from fastapi import FastAPI
import os
import json
import httpx
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

app = FastAPI()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)
converstation_history = [
    {"role": "system", "content": "You are a helpful assistant and you give only answers."}
]
class chatRequest(BaseModel):
    prompt:str

class chatResponse(BaseModel):
    output:str

@app.post("/chat")
def chat(request: chatRequest) -> chatResponse:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role":"user",
                "content":request.prompt
            }
        ],
        model="llama-3.3-70b-versatile"
    )
    
    return chatResponse(
        output=chat_completion.choices[0].message.content
        )





@app.post("/chatHistory")
def chatHistory(request: chatRequest) -> chatResponse:
    converstation_history.append({
        "role":"user",
        "content":request.prompt
    })

    chat_completion = client.chat.completions.create(
        messages=converstation_history,
        model="llama-3.3-70b-versatile"
    )
    assistant_reply = chat_completion.choices[0].message.content
    converstation_history.append({
        "role": "assistant",
        "content": assistant_reply
    })
    return chatResponse(
        output=assistant_reply
        )


@app.delete("/chat/reset")
def delHistory():
    converstation_history.clear()
    converstation_history.append(
        {"role": "system", "content": "You are a helpful assistant and you give only answers."}
    )
    return {"History":"deleted"}

@app.get("/history")
def getHistory():
    return {"history": converstation_history}


@app.post("/chatMore")
async def chatMore(request: chatRequest):

    # 🔹 Build messages array dynamically
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role":"system",
            "content":"return the response only in json inside messages aslo"
        },
        {
            "role": "user",
            "content": request.prompt
        }
    ]

    # 🔹 Call Groq API using httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.7
            }
        )

    result = response.json()

    return {
        "reply": result["choices"][0]["message"]["content"]
    }


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/path")
async def pri():
    return {"message": "Hello World"}
