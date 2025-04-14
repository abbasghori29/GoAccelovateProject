import os
from typing import Dict, Optional, Tuple, List
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import re
from difflib import SequenceMatcher

load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.3
)

# Common LinkedIn geoIDs for major cities/countries
GEOID_MAPPING = {
    # North America
    "united states": "103644278",
    "usa": "103644278",
    "us": "103644278",
    "canada": "101174742",
    "mexico": "103323778",
    
    # Europe
    "united kingdom": "101165590",
    "uk": "101165590",
    "germany": "101282230",
    "france": "105015875",
    "spain": "105646813",
    "italy": "103350119",
    
    # Asia
    "pakistan": "103737379",
    "india": "102713980",
    "china": "102890883",
    "japan": "101355337",
    "singapore": "102454443",
    
    # Middle East
    "uae": "104305776",
    "dubai": "104305776",
    "saudi arabia": "104036028",
    
    # Oceania
    "australia": "101452733",
    "new zealand": "101690313"
}

# Common location aliases and variations
LOCATION_ALIASES = {
    "nyc": ["new york", "new york city"],
    "sf": ["san francisco", "bay area"],
    "la": ["los angeles"],
    "dc": ["washington dc", "washington d.c."],
    "remote": ["work from home", "wfh", "virtual", "online"],
    "karachi": ["khi"],
    "lahore": ["lhr"],
    "islamabad": ["isb"],
    "dubai": ["dxb"],
    "london": ["ldn"],
    "mumbai": ["bombay"],
    "bangalore": ["bengaluru"],
    "hyderabad": ["hyd"]
}

def normalize_location(location: str) -> str:
    """Normalize location string for consistent matching"""
    location = location.lower().strip()
    
    location = re.sub(r'\b(city|town|village|state|province|region|area|district)\b', '', location)
    location = re.sub(r'[^\w\s]', ' ', location)  # Remove special characters
    location = ' '.join(location.split())  # Normalize whitespace
    
    return location

def expand_location_aliases(location: str) -> List[str]:
    """Expand location aliases to their full forms"""
    normalized = normalize_location(location)
    variations = [normalized]
    
    for alias, full_forms in LOCATION_ALIASES.items():
        if alias in normalized:
            variations.extend(full_forms)
    
    return variations

def get_location_similarity(loc1: str, loc2: str) -> float:
    """Calculate similarity between two locations using multiple methods"""
    direct_similarity = SequenceMatcher(None, loc1, loc2).ratio()
    
    words1 = set(loc1.split())
    words2 = set(loc2.split())
    if words1 and words2:
        overlap = len(words1.intersection(words2)) / max(len(words1), len(words2))
    else:
        overlap = 0
    
    contains = 1.0 if loc1 in loc2 or loc2 in loc1 else 0.0
    
    return 0.4 * direct_similarity + 0.3 * overlap + 0.3 * contains

def is_location_match(job_location: str, search_location: str, threshold: float = 0.6) -> bool:
    """Check if a job location matches the search location using semantic matching"""
    if not job_location or not search_location:
        return False
    
    job_loc = normalize_location(job_location)
    search_loc = normalize_location(search_location)
    
    if "remote" in search_loc.lower() and any(term in job_loc.lower() for term in ["remote", "work from home", "wfh", "virtual"]):
        return True
    
    search_variations = expand_location_aliases(search_loc)
    
    max_similarity = max(
        get_location_similarity(job_loc, variation)
        for variation in search_variations
    )
    
    return max_similarity >= threshold

async def get_location_from_llm(location: str) -> Tuple[str, str]:
    """Use Langchain Groq LLM to determine the most relevant country and city from a location query"""
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a location parsing assistant. Given a location query, determine the most relevant country and city. 
            Consider common variations and aliases of locations.
            Return in format 'country,city'. 
            If city is not clear, use the country's capital. 
            If location is unclear, return 'unknown,unknown'.
            For remote work, return 'remote,remote'."""),
            ("human", "Parse this location: {location}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        result = await chain.ainvoke({"location": location})
        
        country, city = result.strip().split(',')
        return country.strip(), city.strip()
    except Exception as e:
        print(f"Error getting location from Langchain Groq LLM: {str(e)}")
        return "unknown", "unknown"

async def get_linkedin_geo_id(location: str) -> Tuple[str, str]:
    """Get the most appropriate LinkedIn geoID for a location"""
    # First try the predefined mapping
    geo_id = get_geo_id_from_mapping(location)
    if geo_id:
        return geo_id, location
    
    
    country, city = await get_location_from_llm(location)
    
    if country == "unknown":
        return "", location  
    
    geo_id = get_geo_id_from_mapping(country)
    if geo_id:
        return geo_id, f"{city}, {country}"
    
    return "", f"{city}, {country}"  

def get_geo_id_from_mapping(location: str) -> Optional[str]:
    """Get geoID from predefined mapping"""
    normalized_location = normalize_location(location)
    return GEOID_MAPPING.get(normalized_location) 