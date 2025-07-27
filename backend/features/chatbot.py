# backend/features/chatbot.py

import json
import requests
from backend import config

def load_knowledge_base():
    """Loads the agricultural rules from our JSON file to give the AI context."""
    try:
        with open('backend/data/agri_knowledge.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

async def generate_chatbot_response(user_message: str, history: list = [], language: str = 'en'):
    """
    Generates a conversational response from the AI chatbot using an improved prompt
    and supporting multiple languages.
    """
    knowledge = load_knowledge_base()
    
    # --- UPGRADED PROMPT ENGINEERING ---
    # This new prompt is much more specific and demanding.
    system_prompt = f"""
    You are 'KrishiMitra', an expert AI agronomist for Indian farmers. 
    Your goal is to provide specific, actionable, and scientifically-grounded advice.

    **Your Instructions:**
    1.  **Respond in the requested language:** The user is asking for a response in '{language}' (e.g., 'en' for English, 'hi' for Hindi). ALL of your output MUST be in this language.
    2.  **Be an Expert:** Do not give vague advice. Provide concrete steps.
    3.  **Use the Knowledge Base:** Your primary source of truth is the provided knowledge base. Refer to it to answer questions about diseases, pests, and farming practices.
    4.  **Provide Actionable Steps:** Instead of saying "monitor your crops," say "Check the underside of the leaves for yellow spots every morning for the next 3 days."
    5.  **Be Practical:** Your advice must be practical for a small-scale farmer in India.
    6.  **Keep it Simple:** Use simple language and format your response with bullet points for clarity. Use emojis where appropriate.

    **Knowledge Base for Your Reference:** {json.dumps(knowledge)}
    """

    # --- Prepare the conversation history for the AI ---
    messages = [{"role": "user", "parts": [{"text": system_prompt}]}]
    for entry in history:
        messages.append({"role": "user", "parts": [{"text": entry["user"]}]})
        messages.append({"role": "model", "parts": [{"text": entry["assistant"]}]})
    
    # Add the latest user message
    messages.append({"role": "user", "parts": [{"text": user_message}]})

    # --- Call the Gemini AI Model ---
    api_key = config.GEMINI_API_KEY
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {"contents": messages}

    try:
        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and result['candidates'][0]['content']['parts'][0]['text']:
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
        else:
            ai_response = "I'm sorry, I'm having a little trouble thinking right now. Please try again."

    except requests.exceptions.RequestException as e:
        print(f"Chatbot AI Error: {e}")
        ai_response = "I can't connect to my brain right now. Please check the connection."

    return {"response": ai_response.strip()}
