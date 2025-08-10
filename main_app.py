import streamlit as st
from datetime import datetime
from gtts import gTTS
import base64
import os
import sys
import json

# Add backend path for imports
sys.path.append('backend')
try:
    from features.govt_schemes import get_schemes_for_farmer
except ImportError:
    def get_schemes_for_farmer(state, farmer_profile, language='en'):
        return {"message": "Government schemes module not available"}

# ------------------ Utility Functions ------------------
def play_audio(text, lang_code='en'):
    tts = gTTS(text=text, lang=lang_code)
    filename = "temp_audio.mp3"
    tts.save(filename)
    with open(filename, "rb") as audio_file:
        audio_bytes = audio_file.read()
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio autoplay="true" controls="controls"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)
    os.remove(filename)

def format_schemes_response(schemes_data):
    """Format the government schemes JSON response for display"""
    if isinstance(schemes_data, dict):
        if "message" in schemes_data:
            return schemes_data["message"]
        
        if "eligible_schemes" in schemes_data:
            schemes = schemes_data["eligible_schemes"]
            if not schemes:
                return "No specific schemes found for your profile. Please check general eligibility criteria."
            
            formatted_text = "🎯 You are eligible for the following government schemes:\n\n"
            for i, scheme in enumerate(schemes, 1):
                scheme_name = scheme.get("name", f"Scheme {i}")
                description = scheme.get("description", "No description available")
                benefit = scheme.get("benefits", "Benefits not specified")
                
                formatted_text += f"**{i}. {scheme_name}**\n"
                formatted_text += f"📋 Description: {description}\n"
                formatted_text += f"💰 Benefits: {benefit}\n\n"
            
            return formatted_text
    
    return "Unable to process schemes data. Please try again."

# ------------------ Language Data ------------------
LANGUAGE_DATA = {
    "English": {
        "welcome": "🌾 Welcome to KrishiMitra!",
        "fertilizer": "🌱 Fertilizer Recommendation",
        "loan": "🏦 Loan/Subsidy Checker",
        "weather_alert": "🌦️ Weather Alerts",
        "crop_calendar": "📅 Crop Calendar",
        "tts_lang": "en"
    },
    "Hindi": {
        "welcome": "🌾 कृषि मित्र में आपका स्वागत है!",
        "fertilizer": "🌱 उर्वरक सिफारिश",
        "loan": "🏦 ऋण/सब्सिडी जांच",
        "weather_alert": "🌦️ मौसम अलर्ट",
        "crop_calendar": "📅 फसल कैलेंडर",
        "tts_lang": "hi"
    },
    "Bhojpuri": {
        "welcome": "🌾 कृषिमित्र में रउआ स्वागत बा!",
        "fertilizer": "🌱 खाद सिफारिश",
        "loan": "🏦 कर्ज/सब्सिडी जांच",
        "weather_alert": "🌦️ मौसम चेतावनी",
        "crop_calendar": "📅 फसल कैलेंडर",
        "tts_lang": "hi"
    },
    "Punjabi": {
        "welcome": "🌾 ਕ੍ਰਿਸ਼ੀ ਮਿਤਰ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ!",
        "fertilizer": "🌱 ਖਾਦ ਸਿਫਾਰਸ਼",
        "loan": "🏦 ਕਰਜ਼ਾ ਜਾਂ ਸਬਸਿਡੀ ਚੈੱਕਰ",
        "weather_alert": "🌦️ ਮੌਸਮ ਚੇਤਾਵਨੀ",
        "crop_calendar": "📅 ਫਸਲ ਕੈਲੰਡਰ",
        "tts_lang": "pa"
    },
    "Tamil": {
        "welcome": "🌾 கிருஷிமித்ராவிற்கு வரவேற்கிறோம்!",
        "fertilizer": "🌱 உர பரிந்துரை",
        "loan": "🏦 கடன்/தொகை சரிபார்ப்பு",
        "weather_alert": "🌦️ வானிலை எச்சரிக்கை",
        "crop_calendar": "📅 பயிர் நாட்காட்டி",
        "tts_lang": "ta"
    },
    "Telugu": {
        "welcome": "🌾 కృషిమిత్రా కు స్వాగతం!",
        "fertilizer": "🌱 ఎరువు సిఫార్సు",
        "loan": "🏦 రుణం/సబ్సిడీ తనిఖీ",
        "weather_alert": "🌦️ వాతావరణ హెచ్చరికలు",
        "crop_calendar": "📅 పంట క్యాలెండర్",
        "tts_lang": "te"
    },
    "Kannada": {
        "welcome": "🌾 ಕೃಷಿ ಮಿತ್ರಕ್ಕೆ ಸ್ವಾಗತ!",
        "fertilizer": "🌱 ರಸಗೊಬ್ಬರ ಶಿಫಾರಸು",
        "loan": "🏦 ಸಾಲ/ಸಬ್ಸಿಡಿ ತಪಾಸಣೆ",
        "weather_alert": "🌦️ ಹವಾಮಾನ ಎಚ್ಚರಿಕೆ",
        "crop_calendar": "📅 ಬೆಳೆ ದಿನದರ್ಶಿ",
        "tts_lang": "kn"
    },
    "Awadhi": {
        "welcome": "🌾 कृषिमित्र मा तोहार स्वागत बा!",
        "fertilizer": "🌱 खाद सिफारिश",
        "loan": "🏦 कर्ज/सब्सिडी जांच",
        "weather_alert": "🌦️ मौसम चेतावनी",
        "crop_calendar": "📅 फसल कैलेंडर",
        "tts_lang": "hi"
    }
}

# ------------------ Sidebar for Language ------------------
st.sidebar.title("🌐 Select Language")
language = st.sidebar.selectbox("Choose your preferred language:", list(LANGUAGE_DATA.keys()))
lang_content = LANGUAGE_DATA[language]

# ------------------ Main UI ------------------
st.title(lang_content["welcome"])

if st.button("🔊 Read Aloud"):
    play_audio(lang_content["welcome"], lang_content["tts_lang"])



# ------------------ Fertilizer Recommendation ------------------
st.header(lang_content["fertilizer"])
crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Maize", "Cereals", "Sugarcane", "Potato", "Tomato"])
soil = st.selectbox("Soil Type", ["Black", "Red", "Sandy", "Brown"])
if st.button("Get Recommendation"):
    rec = f"For {crop} in {soil} soil, use NPK 20:20:0 at 50kg/acre."
    st.success(rec)
    if st.button("🔊 Listen Recommendation"):
        play_audio(rec, lang_content["tts_lang"])

# ------------------ Loan/Subsidy Checker ------------------
st.header(lang_content["loan"])

# Create farmer profile inputs
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Enter your age", min_value=18, max_value=80, value=30)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    state = st.selectbox("Select your State", ["Rajasthan", "Punjab", "Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Other"])

with col2:
    land_holding = st.number_input("Land holding (acres)", min_value=0.0, max_value=100.0, value=2.0, step=0.5)
    is_loanee = st.selectbox("Do you have existing loans?", ["No", "Yes"])

if st.button("Check Eligibility"):
    # Create farmer profile
    farmer_profile = {
        "age": age,
        "gender": gender,
        "land_holding_acres": land_holding,
        "is_loanee": is_loanee.lower() == "yes"
    }
    
    # Get schemes
    try:
        schemes_data = get_schemes_for_farmer(state, farmer_profile, lang_content["tts_lang"])
        formatted_schemes = format_schemes_response(schemes_data)
        st.success(formatted_schemes)
        
        # Store for audio playback
        st.session_state.schemes_text = formatted_schemes
        
    except Exception as e:
        fallback_message = "You are eligible for KCC and PM-KISAN schemes. For detailed information, please visit your nearest agriculture office."
        st.info(fallback_message)
        st.session_state.schemes_text = fallback_message

if st.button("🔊 Listen Eligibility") and hasattr(st.session_state, 'schemes_text'):
    play_audio(st.session_state.schemes_text, lang_content["tts_lang"])

# ------------------ Weather Alerts ------------------
st.header(lang_content["weather_alert"])
today = datetime.now().strftime("%d-%m-%Y")
st.write(f"Today's Date: {today}")
st.warning("⚠️ Heavy Rain Expected in your region today.")

# ------------------ Crop Calendar ------------------
st.header(lang_content["crop_calendar"])
season = st.selectbox("Choose Season", ["Rabi", "Kharif", "Zaid"])
if st.button("Show Calendar"):
    calendar = f"For {season}, sow Wheat, Mustard, and Barley."
    st.success(calendar)
    if st.button("🔊 Listen Calendar"):
        play_audio(calendar, lang_content["tts_lang"])



# ------------------ Mandi Prices ------------------
st.subheader(['Mandi_Data'])
mandi_data ={
    "wheat": "₹2200/qtl",
    "rice": "₹1800/qtl",
    "mustard": "₹5500/qtl",
    "maize": "₹1700/qtl",
    "barley": "₹1600/qtl",
    "soybean": "₹4800/qtl",
    "cotton": "₹6600/qtl",
    "groundnut": "₹5500/qtl",
    "sugarcane": "₹340/qtl",
    "potato": "₹1200/qtl",
    "onion": "₹900/qtl",
    "tomato": "₹1100/qtl",
    "bajra": "₹2150/qtl",
    "jowar": "₹2738/qtl",
    "urad dal": "₹6600/qtl",
    "moong dal": "₹7275/qtl",
    "chana": "₹5400/qtl",
    "masoor dal": "₹6000/qtl",
    "banana": "₹1500/qtl",
    "apple": "₹3000/qtl",
    "brinjal": "₹900/qtl",
    "carrot": "₹1100/qtl",
    "cabbage": "₹850/qtl",
    "peas": "₹1400/qtl"

}
st.table(mandi_data)
# ------------------ Footer ------------------
st.markdown("---")
st.markdown("Made with ❤️ for Indian Farmers - KrishiMitra")






