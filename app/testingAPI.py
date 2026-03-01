import os
import json
from dotenv import load_dotenv
from groq import Groq
print("Saving to:", os.getcwd())

load_dotenv()
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role":"user",
            "content":"Explain the importance of fast language models in 3 line",
        }
    ],
    model="llama-3.3-70b-versatile"
)

print(chat_completion.choices[0].message.content)
with open("/output.json","w") as f:
    json.dump(chat_completion.model_dump(),f,indent=4)
    print("Success -=> output json")


# print(chat_completion.json())