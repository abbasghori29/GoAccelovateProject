from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def create_relevance_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", """You are an expert job matching assistant that analyzes job listings and determines their relevance based on search criteria.
        
        Your task is to analyze job listings and provide a relevance score between 0 and 1, where:
        - 1.0 means perfect match
        - 0.8-0.9 means very good match
        - 0.6-0.7 means good match
        - 0.4-0.5 means partial match
        - 0.0-0.3 means poor match
        
        You should consider:
        - Job title match with desired position
        - Experience requirements match
        - Location match
        - Salary range compatibility
        - Skills match
        - Job nature (onsite/remote/hybrid) match
        
        Format your response as:
        Score: [number between 0 and 1]
        Explanation: [brief explanation of the score]
        """),
        ("human", """
        Job Details:
        Title: {job[job_title]}
        Company: {job[company]}
        Experience: {job[experience]}
        Job Nature: {job[jobNature]}
        Location: {job[location]}
        Salary: {job[salary]}
        
        Search Criteria:
        Position: {search_criteria[position]}
        Experience: {search_criteria[experience]}
        Salary Range: {search_criteria[salary]}
        Job Nature: {search_criteria[jobNature]}
        Location: {search_criteria[location]}
        Skills: {search_criteria[skills]}
        
        Please analyze the relevance of this job listing based on the search criteria.
        """)
    ])

async def analyze_job_relevance(jobs: List[Dict], search_criteria: Dict) -> List[Dict]:
    """Analyze job relevance using Groq and LangChain"""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )
    
    prompt = create_relevance_prompt()
    chain = prompt | llm
    
    relevant_jobs = []
    
    for job in jobs:
        try:
            result = await chain.ainvoke({
                "job": job,
                "search_criteria": search_criteria
            })
            
            # Parse the result to extract score and explanation
            content = result.content
            lines = content.strip().split('\n')
            score = float(lines[0].split(':')[1].strip())
            explanation = lines[1].split(':')[1].strip()
            
            if score >= 0.7:  # Only include jobs with high relevance
                job["relevance_score"] = score
                job["relevance_explanation"] = explanation
                relevant_jobs.append(job)
        except Exception as e:
            print(f"Error analyzing job: {e}")
            continue
    
    # Sort jobs by relevance score
    relevant_jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return relevant_jobs 