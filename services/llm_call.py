import requests
import re
import os
from services.prompt import promptV1
from groq import Groq

# Initialize Groq client
LLM_API_KEY = os.getenv('LLM_API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME', 'llama3-8b-8192')
if not LLM_API_KEY:
    raise EnvironmentError("Missing LLM_API_KEY environment variable.")
client = Groq(api_key=LLM_API_KEY)

def generate_chat_completion(client, prompt, model):
    """Generate chat completion using LLM client."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model = model,
            response_format={"type": "json_object"}
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error generating chat completion: {e}")

def get_pr_chat_completion(prompt, model=MODEL_NAME):
    """
    Main function to generate chat completion.
    Parameters:
        - prompt: (string)
        - Model: (string)
    Returns:
        - Final chat completion (string)
    Raises:
        - RuntimeError for issues in Groq API processing.
    """
    try:
        chat_response = generate_chat_completion(client, prompt, model)
        return chat_response
    except (ConnectionError, RuntimeError) as e:
        print(f"An error occurred: {e}")
        return None
