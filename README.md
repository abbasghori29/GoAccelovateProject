# Job Search Aggregator

A modern web application that aggregates job listings from multiple sources (LinkedIn, Google Jobs) and provides intelligent job matching based on user criteria.

![Search Interface](screenshots/Output1.PNG)

## Features

- **Multi-Source Job Search**: Aggregates jobs from:
  - LinkedIn Jobs
  - Google Jobs
  
- **Smart Job Matching**:
  - Position matching (40% weight)
  - Location matching (20% weight)
  - Skills matching (30% weight)
  - Experience matching (10% weight)

- **Advanced Filtering**:
  - Job title/position
  - Experience level
  - Salary expectations
  - Job nature (Remote/Hybrid/On-site)
  - Location
  - Required skills

![Search Results](screenshots/output2.PNG)

## API Endpoints

### 1. Search Jobs Endpoint
`POST /api/search`

This endpoint handles job search requests and returns matched jobs from multiple sources.

#### Request Body
```json
{
    "position": "AI Engineer",
    "experience": "2",
    "salary": "70000",
    "jobNature": "Hybrid",
    "location": "Karachi,Pakistan",
    "skills": "Python"
}
```

![API Input Example](screenshots/API%20INput.PNG)

#### Response Format
```json
{
    "status": "success",
    "jobs": [
        {
            "job_title": "AI Engineer",
            "company": "Example Corp",
            "experience": "2-3 years",
            "jobNature": "Hybrid",
            "location": "Karachi, Pakistan",
            "salary": "70,000-90,000",
            "apply_link": "https://...",
            "match_score": 85,
            "source": "Google Jobs"
        }
    ],
    "message": "Found X matching jobs"
}
```

### 2. Home Page Endpoint
`GET /`

Returns the main search interface HTML page.

## Job Matching Algorithm

The application uses a scoring system to match jobs with user criteria:

### Scoring Components
1. **Position Match (40%)**
   - Exact match: 40 points
   - Partial match: 30 points

2. **Location Match (20%)**
   - Exact match: 20 points
   - Partial match: 10 points

3. **Skills Match (30%)**
   - Score based on percentage of matched skills
   - Maximum 30 points

4. **Experience Match (10%)**
   - Exact match: 10 points

## Technology Stack

- **Backend**:
  - FastAPI (Python web framework)
  - Async job scraping with aiohttp
  - Pydantic for data validation
  - ScrapingDog API integration

- **Frontend**:
  - HTML5/CSS3
  - Bootstrap 5 for responsive design
  - JavaScript (Vanilla)
  - Font Awesome icons

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
SCRAPINGDOG_API_KEY=your_api_key_here
```

5. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── job_scrapers.py         # Job scraping logic
├── location_handler.py     # Location processing utilities
├── static/                 # Static files
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
├── templates/             # HTML templates
│   └── index.html        # Main application template
└── requirements.txt       # Python dependencies
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your License Here]

