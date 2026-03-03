# app/core/memory.py
# A single shared list that both main.py and StreamSSE.py can import.
# This avoids circular imports — main.py importing from routers and routers
# importing from main.py would cause Python to crash at startup.

conversation_history = [
    {"role": "system", "content": "You are a helpful assistant and you give only answers."}
]
















