import os
from groq import Groq

client = Groq(
    api_key=os.environ.get('GROQ_API_KEY'),
)

def send_to_llm(prompt, code):
    
    print(prompt + code)
    try:
        chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt+'\n'+code,
            }
        ],
        model="llama3-8b-8192",
        )
        print(chat_completion.choices[0].message.content)
        return chat_completion.choices[0].message.content
    except Exception as e:
        return str(e) + (prompt + code)

def llm_code_review(code, prompt_type="style"):
    prompts = {
        "style": "Review this code for any style and formatting issues. List issues by line and provide concise suggestions.",
        "bug": "Analyze this code for any potential bugs. Describe issues with line numbers and suggest concise ways to fix them.",
        "performance": "Review this code for any performance improvements. Suggest optimizations for inefficient patterns in one line.",
        "best_practices": "Check this code for adherence to best practices. List any recommendations you have in less that 25 words."
    }

    prompt = prompts.get(prompt_type, prompts["style"])

    response = send_to_llm(prompt, code)

    return response


