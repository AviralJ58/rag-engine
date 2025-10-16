from google import genai
from google.genai.types import HttpOptions
import os
from dotenv import load_dotenv

load_dotenv()

USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")

# Initialize once to reuse (avoid reloading model on every query)
client = genai.Client(http_options=HttpOptions(api_version="v1"), api_key=API_KEY, vertexai=USE_VERTEXAI)

def generate_response(messages):
    """Call the local transformer model with messages."""
    try:
        # Extract text content from OpenAI-style messages
        prompt_text = "\n".join([m["content"] for m in messages if "content" in m])

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_text,  # pass a string instead of list of dicts
        )
        return response.text if response else "No response"
    except Exception as e:
        return f"LLM error: {e}"
