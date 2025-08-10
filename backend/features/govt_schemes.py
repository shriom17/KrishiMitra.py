# backend/features/govt_schemes.py

import json
from typing import Optional

def load_schemes_data(language: str = 'en'):
    """
    Loads the government schemes data from a language-specific JSON file.
    """
    import os
    
    # Try different possible paths for the JSON file
    possible_paths = [
        f'backend/data/govt_schemes_{language}.json',
        f'data/govt_schemes_{language}.json',
        f'govt_schemes_{language}.json',
        os.path.join(os.path.dirname(__file__), '..', 'data', f'govt_schemes_{language}.json')
    ]
    
    for filename in possible_paths:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    
    print(f"Warning: govt_schemes_{language}.json not found in any expected location.")
    return {}

def check_eligibility(scheme: dict, farmer_profile: dict) -> bool:
    """
    Checks if a farmer is eligible for a given scheme based on their profile.
    """
    criteria = scheme.get("eligibility_criteria", {})
    
    # Check gender criteria
    if "gender" in criteria and farmer_profile.get("gender"):
        if criteria["gender"].lower() != farmer_profile["gender"].lower():
            return False
            
    # Check land holding criteria
    if "min_land_holding_acres" in criteria and farmer_profile.get("land_holding_acres"):
        if farmer_profile["land_holding_acres"] < criteria["min_land_holding_acres"]:
            return False
            
    # Check if the farmer is a loanee
    if "is_loanee" in criteria and farmer_profile.get("is_loanee") is not None:
        if criteria["is_loanee"] != farmer_profile["is_loanee"]:
            return False
            
    # If all checks pass, the farmer is eligible
    return True

def get_schemes_for_farmer(state: str, farmer_profile: dict, language: str = 'en'):
    """
    Retrieves a personalized list of government schemes a farmer is eligible for.
    """
    all_schemes_data = load_schemes_data(language)
    
    # Combine national and state-specific schemes into one list
    national_schemes = all_schemes_data.get("national_schemes", [])
    state_schemes = all_schemes_data.get("state_specific_schemes", {}).get(state.title(), [])
    all_available_schemes = national_schemes + state_schemes
    
    # Filter the schemes based on the farmer's profile
    eligible_schemes = [
        scheme for scheme in all_available_schemes 
        if check_eligibility(scheme, farmer_profile)
    ]
    
    if not eligible_schemes:
        return {"message": "Based on the provided profile, no specific schemes were found. Please check the general list."}
        
    return {
        "query": {
            "state": state,
            "language": language,
            "farmer_profile": farmer_profile
        },
        "eligible_schemes": eligible_schemes
    }
