import requests
import re
import os
from prompt import promptV1
from groq import Groq

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise EnvironmentError("Missing GROQ_API_KEY environment variable.")
client = Groq(api_key=GROQ_API_KEY)

def generate_chat_completion(client, prompt, model_name=None):
    """Generate chat completion using Groq client."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model = model_name if model_name else "llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error generating chat completion: {e}")

def get_pr_chat_completion(prompt, model=None):
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
