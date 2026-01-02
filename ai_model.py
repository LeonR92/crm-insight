import os

from dotenv import load_dotenv
from pydantic_ai.models.mistral import MistralModel

from config import AI_MODEL

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")


model = MistralModel(AI_MODEL)
