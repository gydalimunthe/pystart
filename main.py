from groq_connector import get_groq_response
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


class ChatRequest(BaseModel):
    prompt: str


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = get_groq_response(request.prompt)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc
    return {"response": response}


if __name__ == "__main__":
    while True :
        user_input = input('Ask me anything (type "quit" to exit): ')
        if user_input == 'quit' :
            break
        
        response = get_groq_response(user_input)
        print(response)
