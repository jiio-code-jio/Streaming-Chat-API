## Streaming Chat APP
- This is simple Chat App 
1. Here i have used groq API it is free for now but in the future we many not know.
2. This has many endpoints like history,chat,chatHistory,chatMore

"history" : endpoint gets the total history use chat with model in chatHistory endpoint

"chatMore": this endpoint is for arrays of instructions calls and to use aysnc calls 

"chat" : this endpoint is for temporary chat where history is not saved

"chatHistory" : this endpoint is chat history is active. It is stores the data in json and each time the history is passed for API calls 


Note : This is in-memory history if the applications restart it goes away
and it is limitated to per process not for per person 


#### In Phase E we completed streaming with SSE
- We created a function 