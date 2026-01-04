import os

import dspy
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

lm = dspy.LM(
    "mistral/mistral-large-latest",
    api_key=api_key,
    temperature=0.7,
)
dspy.configure(lm=lm)


class Assistant(dspy.Signature):
    """Be a friendly assistant and answer the user warmly."""

    question = dspy.InputField()
    answer = dspy.OutputField()


bot = dspy.ChainOfThought(Assistant)


if __name__ == "__main__":
    response = bot(question="How's the weather in Paris?")

    print(f"REASONING: {response.reasoning}")
    print(f"ANSWER: {response.answer}")

    print("\n--- THE PROMPT DSPY ENGINEERED ---")
    lm.inspect_history(n=1)
