import os

from dotenv import load_dotenv
from pydantic_ai.models.mistral import MistralModel

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
AI_MODEL = "ministral-14b-2512"

model = MistralModel(AI_MODEL)


TEMPERATURE = 0
