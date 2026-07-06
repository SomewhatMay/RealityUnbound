import openai
from pathlib import Path
from config import MODEL

token_exists = False
tokens = None
if Path("./tokens.py"):
    try:
        import tokens
        token_exists = True
        openai.api_key = tokens.openAIToken()
    except:
        print("There was an error loading OpenAI token!")
else:
    print("No tokens.py")


def set_api_key(token):
    openai.api_key = tokens.openAIToken(token)


def fetch_completion(messages):
    return openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
        stop=None,
        top_p=0.8,
    )
