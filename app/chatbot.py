from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.rag import get_answer

router = APIRouter()

templates = Jinja2Templates(directory="templates")


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@router.get("/chatbot", response_class=HTMLResponse)
def chatbot_page(request: Request):
    if not request.session.get("username"):
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="chatbot.html",
        context={
            "request": request,
            "username": request.session.get("username", "User")
        }
    )

@router.post("/chat")
def chat(data: ChatRequest, request: Request):
    if not request.session.get("username"):
        raise HTTPException(status_code=401, detail="Please log in to use the chatbot")

    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question cannot be blank")

    try:
        answer = get_answer(question)

        return {"answer": answer}

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="The assistant is temporarily unavailable. Please try again.")
