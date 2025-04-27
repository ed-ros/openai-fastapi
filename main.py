import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from openai import OpenAI
import uuid
import re
import html
import markdown

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



def format_code_blocks(text):
    def replacer(match):
        code = match.group(1)
        escaped_code = html.escape(code)  # Escapa <, >, &, etc
        return f"<pre><code>{escaped_code}</code></pre>"
    
    return re.sub(r"```(.*?)```", replacer, text, flags=re.DOTALL)
    
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    session_id = str(uuid.uuid4())
    return templates.TemplateResponse("index.html", {"request": request, "session_id": session_id, "result": None})

@app.post("/chat", response_class=HTMLResponse)
async def post_form(request: Request, user_input: str = Form(...), session_id: str = Form(...)):

    conversation = conversations.get(session_id)
    if conversation is None:
        conversation = [{"role": "system", "content": "You are an expert in all banana and chimpanzee related topics. You are also a bit funny, but don't use emojis. Don't make every conversation about banana and chimpanzee, just add subtle hints about it. Consider adding some interesting trivia about bananas or chimpanzees, but make an interesting connection to the current subject. Use markdown."}]
    
    conversation.append({"role": "user", "content": user_input})
    
    TEST_MODE = False
    
    if TEST_MODE:
        openai_reply = f"(fake answer)"
    else:
        # Call OpenAI API with user's input
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation
        )

        # Get the response text
        openai_reply = response.choices[0].message.content.strip()
        openai_reply = format_code_blocks(openai_reply)
        openai_reply = markdown.markdown(openai_reply)
        
    conversation.append({"role": "assistant", "content": openai_reply})
    
    conversations[session_id] = conversation
    
    # Return page with OpenAI reply
    return templates.TemplateResponse("index.html", {"request": request, "session_id": session_id, "conversation": conversation})
