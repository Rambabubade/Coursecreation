import requests
import json
import os
import re
from Secret_Key import api_key
Api_Key = os.getenv('api_key')
# Load the API key from an environment variable


def get_answer(question):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": question}
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s.,!?;:]', '', text)
    return text

if __name__ == "__main__":
    question = input("Please enter your question: ")
    answer = get_answer(question)
    
    if answer:
        # Check the structure of the response to access the generated text
        try:
            generated_text = answer['candidates'][0]['content']['parts'][0]['text']
            # Clean the generated answer
            cleaned_answer = clean_text(generated_text)
            print("Answer:", cleaned_answer)
        except (IndexError, KeyError):
            print("No text generated or unexpected response structure.")
