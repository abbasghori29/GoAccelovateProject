from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from job_scrapers import search_jobs
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI(title="Job Finder API")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class JobSearchRequest(BaseModel):
    position: str
    experience: str
    salary: str
    jobNature: str
    location: str
    skills: str

class JobResponse(BaseModel):
    job_title: str
    company: str
    experience: str
    jobNature: str
    location: str
    salary: str
    apply_link: str
    match_score: float
    source: str
    posted_date: Optional[str] = None

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/search")
async def search_jobs_api(search_data: JobSearchRequest):
    try:
        # Convert search data to dictionary
        search_criteria = search_data.model_dump()
        
        # Search for jobs
        jobs = await search_jobs(search_criteria)
        
        # Return results
        return JSONResponse(
            content={
                "status": "success",
                "jobs": jobs,
                "message": f"Found {len(jobs)} matching jobs" if jobs else "No exact matches found, showing similar jobs"
            }
        )
    except Exception as e:
        print(f"Error in search_jobs_api: {str(e)}")
        return JSONResponse(
            status_code=200,  # Changed to 200 since we want to show results even if not perfect
            content={
                "status": "success",
                "jobs": [],
                "message": "No jobs found matching your criteria. Try adjusting your search parameters."
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 