"""
Ollama Helper for the app.
Handles communication with a locally running Ollama API to generate AI recommendations (download the Ollama app beforehand is MANDATORY for the app to work).
Default model: "mistral"
"""

import requests
import json


def get_ai_recommendation(prompt, model="mistral"):
    """
    Send a prompt to the Ollama API and return the generated recommendation.

    Parameters:
        prompt (str): The text prompt to send to the AI model
        model (str): The model name to use (default = "mistral")

    Returns:
        str: AI-generated recommendation text
             If the API is unavailable, returns a fallback message with error details.

    Process:
        - POST request to Ollama API endpoint: http://localhost:11434/api/generate
        - Stream response line by line
        - Collect "response" field from each JSON line
        - Concatenate into final output string
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt},
            stream=True
        )
        output = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    output += data["response"]
        return output.strip()
    except Exception as e:
        # Fallback if API is unavailable or request fails
        return f"(AI unavailable, fallback used: {e})"