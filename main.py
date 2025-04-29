import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI
import uuid
import re
import html

load_dotenv() 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# in-memory store for user conversations
conversations = {}

# Set up OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
)
    
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    session_id = str(uuid.uuid4())
    return templates.TemplateResponse("index.html", {"request": request, "session_id": session_id, "result": None})

@app.post("/chat", response_class=HTMLResponse)
async def post_form(request: Request, user_input: str = Form(...), session_id: str = Form(...)):

    conversation = conversations.get(session_id)
    if conversation is None:
        conversation = [{"role": "system", "content": "You sometimes like to drop some interesting and related quotes. You are also a bit funny, but don't use emojis. Consider adding some interesting trivia about the subject being discussed."}]
    
    conversation.append({"role": "user", "content": user_input})
    
    def stream_openai_response():
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            stream=True,
        )
        
        openai_reply = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                piece = chunk.choices[0].delta.content
                openai_reply += piece
                yield piece
            
        # after streaming is done
        conversation.append({"role": "assistant", "content": openai_reply})
        conversations[session_id] = conversation

    return StreamingResponse(stream_openai_response(), media_type="text/html")
