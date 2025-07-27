# backend/main.py
# backend/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field # <-- NEW IMPORTS for farmer profile
from typing import List, Optional     # <-- NEW IMPORTS for farmer profile

from backend.features import weather
from backend.features import agri_advisor
from backend.features import location_info
from backend.features import mandi_prices
from backend.features import disease_detection
from backend.features import govt_schemes # <-- This will use your new personalized logic
from backend.features import tts
from backend.features import chatbot

# Create the app instance
app = FastAPI()

# --- Pydantic Models for API Request Bodies ---
class ChatMessage(BaseModel):
    user: str
    assistant: str

class ChatRequest(BaseModel):
    user_message: str
    history: List[ChatMessage] = []

class FarmerProfile(BaseModel):
    """Defines the data structure for a farmer's profile."""
    gender: Optional[str] = None
    land_holding_acres: Optional[float] = Field(None, gt=0)
    is_loanee: Optional[bool] = None
    # We can add more fields here later as you suggested (age, category, etc.)


@app.get("/")
def read_root():
    return {"Project": "KrishiMitra 2.0+ Backend"}

# --- All previous endpoints ---
@app.get("/api/v1/weather")
def get_weather(city: str = "Udaipur", state: str = "Rajasthan"):
    weather_data = weather.get_weather_data(city, state)
    return weather_data

@app.get("/api/v1/agri_advice")
async def get_agri_advice(city: str = "Udaipur", state: str = "Rajasthan", crop: str = "wheat"):
    advice_data = await agri_advisor.generate_agri_advice(city, state, crop)
    return advice_data

@app.get("/api/v1/crop_recommendation")
def get_crop_recommendation(city: str = "Udaipur", state: str = "Rajasthan"):
    recommended_crops = location_info.get_recommended_crops(city, state)
    zone_name = location_info.get_agro_climatic_zone_name(city, state)
    return {
        "location": { "city": city, "state": state, "agro_climatic_zone": zone_name },
        "recommended_crops": recommended_crops
    }

@app.get("/api/v1/mandi_prices")
def get_mandi_prices(state: str = "Rajasthan", commodity: str = "Wheat"):
    price_data = mandi_prices.get_live_prices_for_commodity(state, commodity)
    return price_data

@app.post("/api/v1/detect_disease")
async def detect_disease(image: UploadFile = File(...)):
    result = disease_detection.simulate_disease_detection(image)
    return result

@app.get("/api/v1/generate_audio")
def generate_audio(text: str = "Welcome to KrishiMitra", lang: str = "en"):
    audio_stream = tts.generate_audio_from_text(text, lang)
    if audio_stream:
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    else:
        return {"error": "Could not generate audio."}

@app.post("/api/v1/chatbot")
async def handle_chat(chat_request: ChatRequest):
    history_dicts = [item.dict() for item in chat_request.history]
    response = await chatbot.generate_chatbot_response(
        user_message=chat_request.user_message,
        history=history_dicts
    )
    return response

# --- UPGRADED: Personalized Government Schemes Endpoint ---
@app.post("/api/v1/govt_schemes")
def get_govt_schemes(profile: FarmerProfile, state: str = "Rajasthan", lang: str = "en"):
    """
    This endpoint provides a personalized list of government schemes
    based on the farmer's profile.
    """
    # Convert the Pydantic model to a simple dictionary for our logic function
    farmer_profile_dict = profile.dict(exclude_none=True)
    
    schemes_data = govt_schemes.get_schemes_for_farmer(state, farmer_profile_dict, lang)
    return schemes_data
