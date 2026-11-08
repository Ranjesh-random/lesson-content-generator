import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

llm = ChatGroq(
    model=MODEL_NAME,
    temperature=0.2,
    api_key=GROQ_API_KEY
)