import os
import aiohttp
import asyncio
from typing import Dict, List
from dotenv import load_dotenv
from location_handler import get_linkedin_geo_id, is_location_match
from difflib import SequenceMatcher

load_dotenv()

SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")

def normalize_text(text: str) -> str:
    """Simple text normalization without NLTK"""
    if not text:
        return ""
    return ' '.join(text.lower().split())

def calculate_match_score(job: Dict, search_criteria: Dict) -> int:
    """Calculate match score between job and search criteria"""
    score = 0
    
    # Normalize all text for comparison
    job_title = normalize_text(job.get("job_title", ""))
    search_position = normalize_text(search_criteria.get("position", ""))
    job_location = normalize_text(job.get("location", ""))
    search_location = normalize_text(search_criteria.get("location", ""))
    job_skills = normalize_text(job.get("skills", ""))
    search_skills = normalize_text(search_criteria.get("skills", ""))
    
    # Position match (40 points)
    if search_position:
        # Check for partial matches
        if search_position in job_title:
            score += 40
        elif any(word in job_title for word in search_position.split()):
            score += 30
    
    # Location match (20 points)
    if search_location:
        if search_location in job_location:
            score += 20
        elif any(word in job_location for word in search_location.split()):
            score += 10
    
    # Skills match (30 points)
    if search_skills:
        matched_skills = sum(1 for skill in search_skills.split() if skill in job_skills)
        if matched_skills > 0:
            score += min(30, (matched_skills / len(search_skills.split())) * 30)
    
    # Experience match (10 points)
    job_exp = normalize_text(job.get("experience", ""))
    search_exp = normalize_text(search_criteria.get("experience", ""))
    if search_exp and search_exp in job_exp:
        score += 10
    
    # Ensure minimum score for any job
    return max(10, min(100, score))

def is_location_match(job_location: str, search_location: str) -> bool:
    """Check if job location matches search location"""
    if not search_location:
        return True
    
    job_loc = normalize_text(job_location)
    search_loc = normalize_text(search_location)
    
    # Check for exact match or if search location is contained in job location
    return search_loc in job_loc

async def scrape_linkedin(session: aiohttp.ClientSession, search_criteria: Dict) -> List[Dict]:
    """Scrape LinkedIn jobs with proper error handling"""
    url = "https://api.scrapingdog.com/linkedinjobs/"
    
    # Get appropriate geoID for the location
    geo_id, normalized_location = await get_linkedin_geo_id(search_criteria["location"])
    
    params = {
        "api_key": SCRAPINGDOG_API_KEY,
        "field": search_criteria["position"],
        "page": "1"
    }
    
    if geo_id:
        params["geoid"] = geo_id
    
    try:
        print(f"Fetching LinkedIn jobs with params: {params}")
        async with session.get(url, params=params) as response:
            if response.status == 200:
                jobs = await response.json()
                if isinstance(jobs, list):
                    print(f"LinkedIn returned {len(jobs)} jobs")
                    
                    matched_jobs = []
                    for job in jobs:
                        job_dict = {
                            "job_title": job.get("title", ""),
                            "company": job.get("company", ""),
                            "experience": job.get("experience", ""),
                            "jobNature": search_criteria["jobNature"],
                            "location": job.get("location", ""),
                            "salary": job.get("salary", ""),
                            "apply_link": job.get("link", ""),
                            "posted_date": job.get("date", ""),
                            "source": "LinkedIn"
                        }
                        
                        # Check if job location matches search location
                        if is_location_match(job_dict["location"], normalized_location):
                            job_dict["match_score"] = calculate_match_score(job_dict, search_criteria)
                            matched_jobs.append(job_dict)
                    
                    print(f"LinkedIn matched jobs found: {len(matched_jobs)}")
                    return matched_jobs
                else:
                    print(f"LinkedIn returned unexpected format: {type(jobs)}")
            elif response.status == 400:
                error_data = await response.json()
                print(f"LinkedIn API error (400): {error_data.get('message', 'Invalid API key or parameters')}")
            else:
                print(f"LinkedIn API error: {response.status}")
    except Exception as e:
        print(f"Error scraping LinkedIn: {str(e)}")
    
    return []

async def scrape_indeed(session: aiohttp.ClientSession, search_criteria: Dict) -> List[Dict]:
    """Scrape Indeed jobs with proper error handling"""
    url = "https://api.scrapingdog.com/indeed/"
    
    # Get normalized location
    _, normalized_location = await get_linkedin_geo_id(search_criteria["location"])
    
    params = {
        "api_key": SCRAPINGDOG_API_KEY,
        "query": f"{search_criteria['position']} {normalized_location}",
        "location": normalized_location,
        "page": "1"
    }
    
    try:
        print(f"Fetching Indeed jobs with params: {params}")
        async with session.get(url, params=params) as response:
            if response.status == 200:
                jobs = await response.json()
                if isinstance(jobs, list):
                    print(f"Indeed returned {len(jobs)} jobs")
                    
                    matched_jobs = []
                    for job in jobs:
                        job_dict = {
                            "job_title": job.get("title", ""),
                            "company": job.get("company", ""),
                            "experience": job.get("experience", ""),
                            "jobNature": search_criteria["jobNature"],
                            "location": job.get("location", ""),
                            "salary": job.get("salary", ""),
                            "apply_link": job.get("link", ""),
                            "posted_date": job.get("date", ""),
                            "source": "Indeed"
                        }
                        
                        if is_location_match(job_dict["location"], normalized_location):
                            job_dict["match_score"] = calculate_match_score(job_dict, search_criteria)
                            matched_jobs.append(job_dict)
                    
                    print(f"Indeed matched jobs found: {len(matched_jobs)}")
                    return matched_jobs
                else:
                    print(f"Indeed returned unexpected format: {type(jobs)}")
            elif response.status == 400:
                error_data = await response.json()
                print(f"Indeed API error (400): {error_data.get('message', 'Invalid API key or parameters')}")
            else:
                print(f"Indeed API error: {response.status}")
    except Exception as e:
        print(f"Error scraping Indeed: {str(e)}")
    
    return []

async def scrape_google_jobs(session: aiohttp.ClientSession, search_criteria: Dict) -> List[Dict]:
    """Scrape Google jobs with proper error handling"""
    url = "https://api.scrapingdog.com/google_jobs/"
    
    _, normalized_location = await get_linkedin_geo_id(search_criteria["location"])
    
    params = {
        "api_key": SCRAPINGDOG_API_KEY,
        "query": f"{search_criteria['position']} {normalized_location}",
        "location": normalized_location,
        "page": "1"
    }
    
    try:
        print(f"Fetching Google jobs with params: {params}")
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                
                if not isinstance(data, dict):
                    print(f"Google Jobs returned unexpected format: {type(data)}")
                    return []
                
                jobs = data.get("jobs_results", [])
                if not isinstance(jobs, list):
                    print(f"Google Jobs jobs_results has unexpected format: {type(jobs)}")
                    return []
                
                print(f"Google Jobs returned {len(jobs)} jobs")
                
                matched_jobs = []
                for job in jobs:
                    job_dict = {
                        "job_title": job.get("title", ""),
                        "company": job.get("company_name", ""),
                        "jobNature": search_criteria["jobNature"],
                        "location": job.get("location", ""),
                        "source": "Google Jobs"
                    }
                    
                    # Handle nested fields safely
                    if isinstance(job.get("detected_extensions"), dict):
                        job_dict["experience"] = job["detected_extensions"].get("experience", "")
                        job_dict["salary"] = job["detected_extensions"].get("salary", "")
                        job_dict["posted_date"] = job["detected_extensions"].get("posted_at", "")
                        job_dict["jobNature"] = job["detected_extensions"].get("work_type", search_criteria["jobNature"])
                    
                    if isinstance(job.get("via"), list) and len(job["via"]) > 0:
                        if isinstance(job["via"][0], dict):
                            job_dict["apply_link"] = job["via"][0].get("link", "")
                    
                    # Check if job location matches search location
                    if is_location_match(job_dict["location"], normalized_location):
                        job_dict["match_score"] = calculate_match_score(job_dict, search_criteria)
                        matched_jobs.append(job_dict)
                
                print(f"Google Jobs matched jobs found: {len(matched_jobs)}")
                return matched_jobs
            elif response.status == 400:
                error_data = await response.json()
                print(f"Google Jobs API error (400): {error_data.get('message', 'Invalid API key or parameters')}")
            else:
                print(f"Google Jobs API error: {response.status}")
    except Exception as e:
        print(f"Error scraping Google Jobs: {str(e)}")
    
    return []

async def search_jobs(search_criteria: Dict) -> List[Dict]:
    """Search for jobs across multiple platforms"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            scrape_linkedin(session, search_criteria),
            scrape_google_jobs(session, search_criteria)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_jobs = []
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                print(f"Error in one of the scrapers: {str(result)}")
                continue
        
        if not all_jobs:
            return []
            
        all_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return all_jobs[:20] 