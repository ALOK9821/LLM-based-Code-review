def llm_code_review(code, prompt_type="style"):
    prompts = {
        "style": "Please review this code for any style and formatting issues. List issues by line and provide suggestions.",
        "bug": "Analyze this code for any potential bugs. Describe issues with line numbers and suggest ways to fix them.",
        "performance": "Review this code for any performance improvements. Suggest optimizations for inefficient patterns.",
        "best_practices": "Check this code for adherence to best practices. List any recommendations you have."
    }

    prompt = prompts.get(prompt_type, prompts["style"])

    response = send_to_llm(prompt, code)

    return response

def send_to_llm(prompt, code):
    simulated_response = f"Simulated LLM response for prompt: {prompt}\n\nCode:\n{code[:200]}..."  # Only show first 200 chars
    return simulated_response
