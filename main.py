import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv() 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, user_input: str = Form(...)):
    # Call OpenAI API with user's input
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in all banana and chimpanzee related topics. You are also a bit funny, but don't use emojis. Don't make every conversation about banana and chimpanzee, just add subtle hints about it. Consider adding some interesting trivia about bananas or chimpanzees, but make an interesting connection to the current subject."},
            {"role": "user", "content": user_input},
        ],
    )

    # Get the response text
    openai_reply = response.choices[0].message.content.strip()

    # Return page with OpenAI reply
    return templates.TemplateResponse("index.html", {"request": request, "result": openai_reply})
