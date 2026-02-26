from groq_connector import get_groq_response
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

if __name__ == "__main__":
    while True :
        user_input = input('Ask me anything (type "quit" to exit): ')
        if user_input == 'quit' :
            break
        
        response = get_groq_response(user_input)
        print(response)
