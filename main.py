from pydantic_ai import Agent, ModelSettings

from ai_model import model
from config import TEMPERATURE

hello_world_agent = Agent(
    model,
    system_prompt="Be a friendly assistant",
    model_settings=ModelSettings(temperature=TEMPERATURE),
)


if __name__ == "__main__":
    print(hello_world_agent.run_sync("Who are you?"))
