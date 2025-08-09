# backend/features/agri_advisor.py

import json
import requests
from backend.features import weather
from backend.features import location_info
from backend.features import rule_engine # Will use the new stage-aware version
from backend import config

async def generate_agri_advice(city: str, state: str, crop: str, crop_stage: str, lang: str = 'en'):
    """
    Generates farming advice that is now aware of the crop's growth stage.
    """
    agro_climatic_zone = location_info.get_agro_climatic_zone_name(city, state)
    weather_data = weather.get_weather_data(city, state)
    if "error" in weather_data:
        return {"error": "Could not fetch weather data to generate advice."}

    # Call the upgraded rule engine with the crop_stage
    rule_based_advice = rule_engine.generate_rule_based_advice(weather_data, crop, crop_stage)

    # --- Upgraded Prompt Engineering with Crop Stage ---
    prompt = f"""
    You are an expert AI agronomist for Indian farmers. Your task is to convert structured advice into a simple, conversational summary and add productivity tips.

    CRITICAL INSTRUCTION: You MUST generate your entire response in the language with the code '{lang}'.

    **Context:**
    - Location: {city}, {state}, India
    - Agro-Climatic Zone (ACZ): {agro_climatic_zone}
    - Farmer's Crop: {crop}
    - Current Crop Stage: {crop_stage}
    - Current Weather: {json.dumps(weather_data)}
    - Structured Advice Points: {json.dumps(rule_based_advice)}

    **Instructions:**
    1.  Summarize the most critical advice from the structured points in simple, bullet-point format.
    2.  After the summary, add a new section called 'Productivity Tips'.
    3.  In the 'Productivity Tips' section, provide one additional, general tip for the specified '{crop}' at its current '{crop_stage}' to help increase yield or quality.
    4.  Keep the language simple and direct. Use emojis.
    """

    api_key = config.GEMINI_API_KEY 
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}

    try:
        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        ai_summary = result['candidates'][0]['content']['parts'][0]['text'] if 'candidates' in result else "Could not generate AI summary."

    except requests.exceptions.RequestException as e:
        print(f"AI API Error: {e}")
        ai_summary = "Could not connect to the AI service."

    return {
        "agro_climatic_zone": agro_climatic_zone,
        "live_weather": weather_data,
        "ai_summary": ai_summary.strip()
    }
