from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
import uuid
import asyncio
from pathlib import Path
import tempfile
import PyPDF2
import io

# Import your agent classes
from agent import CVOptimizer, JobAnalysis, ProfileAnalysis, GapAnalysis, CVSection

app = FastAPI(title="CV Optimizer API", version="1.0.0")

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
sessions = {}
uploaded_files = {}

# Pydantic models for API
class JobDescriptionRequest(BaseModel):
    cv_id: str
    job_description: str

class UserAnswersRequest(BaseModel):
    analysis_id: str
    confirmed_skills: List[str]

class TemplateRequest(BaseModel):
    analysis_id: str
    template_id: str

# Initialize CV Optimizer
optimizer = CVOptimizer()

# Helper function to extract text from PDF
def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

@app.get("/")
async def root():
    return {"message": "CV Optimizer API is running"}

@app.post("/api/upload-cv")
async def upload_cv(cv_file: UploadFile = File(...)):
    """Upload CV file and extract text"""
    
    # Validate file type
    if cv_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate unique CV ID
    cv_id = str(uuid.uuid4())
    
    try:
        # Read file content
        content = await cv_file.read()
        
        # Extract text from PDF
        cv_text = extract_text_from_pdf(content)
        
        # Store in memory (replace with database in production)
        uploaded_files[cv_id] = {
            "filename": cv_file.filename,
            "content": content,
            "text": cv_text,
            "upload_time": str(asyncio.get_event_loop().time())
        }
        
        return {
            "cv_id": cv_id,
            "message": "CV uploaded successfully",
            "filename": cv_file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CV: {str(e)}")

@app.post("/api/analyze")
async def analyze_job_description(request: JobDescriptionRequest):
    """Analyze job description against uploaded CV"""
    
    # Check if CV exists
    if request.cv_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="CV not found")
    
    cv_data = uploaded_files[request.cv_id]
    cv_text = cv_data["text"]
    
    try:
        # Step 1: Analyze job offer
        job_analysis = optimizer.job_analyzer.analyze_job_offer(request.job_description)
        
        # Step 2: Analyze profile
        profile_analysis = optimizer.profile_analyzer.analyze_profile(cv_text, job_analysis)
        
        # Step 3: Check if additional input needed
        is_sufficient, gap_analysis = optimizer.gap_analyzer.analyze_gaps(profile_analysis)
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Store session data
        sessions[analysis_id] = {
            "cv_id": request.cv_id,
            "job_description": request.job_description,
            "job_analysis": job_analysis.model_dump(),
            "profile_analysis": profile_analysis.model_dump(),
            "gap_analysis": gap_analysis.model_dump() if gap_analysis else None,
            "is_sufficient": is_sufficient
        }
        
        # Prepare response based on frontend expectations
        response_data = {
            "analysis_id": analysis_id,
            "overall_match": profile_analysis.relevance_score_overall,
            "skills_match": max(profile_analysis.skills_match.values()) if profile_analysis.skills_match else 50,
            "experience_match": profile_analysis.relevance_score_overall + 10,  # Simulate higher experience match
            "recommendations": profile_analysis.recommendations
        }
        
        # Add gap analysis if needed
        if gap_analysis:
            response_data.update({
                "overall_analysis": gap_analysis.overall_analysis,
                "missing_skills": gap_analysis.missing_skills
            })
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze job: {str(e)}")

@app.post("/api/generate-resume")
async def generate_optimized_resume(request: UserAnswersRequest):
    """Generate optimized resume with user confirmed skills"""
    
    # Check if analysis exists
    if request.analysis_id not in sessions:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    session_data = sessions[request.analysis_id]
    
    try:
        # Reconstruct objects from stored data
        job_analysis = JobAnalysis(**session_data["job_analysis"])
        profile_analysis = ProfileAnalysis(**session_data["profile_analysis"])
        
        # Generate CV sections
        cv_sections = optimizer.cv_generator.generate_cv_sections(
            job_analysis=job_analysis,
            profile_analysis=profile_analysis,
            user_confirmed_skills=request.confirmed_skills
        )
        
        # Save optimized CV data
        optimized_cv_data = cv_sections.model_dump()
        
        # Store for potential download
        sessions[request.analysis_id]["optimized_cv"] = optimized_cv_data
        
        # Create JSON file for template system
        output_file = f"optimized_cv_{request.analysis_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(optimized_cv_data, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "message": "Optimized CV generated successfully",
            "cv_data": optimized_cv_data,
            "download_url": f"/api/download/{request.analysis_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CV: {str(e)}")

@app.get("/api/download/{analysis_id}")
async def download_optimized_cv(analysis_id: str):
    """Download the optimized CV JSON file"""
    
    if analysis_id not in sessions:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    file_path = f"optimized_cv_{analysis_id}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="CV file not found")
    
    return FileResponse(
        path=file_path,
        filename=f"optimized_cv_{analysis_id}.json",
        media_type="application/json"
    )

@app.get("/api/templates")
async def get_available_templates():
    """Get list of available CV templates"""
    
    # Mock templates - replace with actual template data
    templates = [
        {
            "id": "professional",
            "name": "Professional",
            "description": "A clean, professional template with a traditional layout",
            "thumbnailUrl": "https://via.placeholder.com/300x400?text=Professional"
        },
        {
            "id": "modern",
            "name": "Modern",
            "description": "A contemporary design with bold elements and creative layout",
            "thumbnailUrl": "https://via.placeholder.com/300x400?text=Modern"
        },
        {
            "id": "technical",
            "name": "Technical",
            "description": "Optimized for technical roles with focus on skills and projects",
            "thumbnailUrl": "https://via.placeholder.com/300x400?text=Technical"
        },
        {
            "id": "executive",
            "name": "Executive",
            "description": "Elegant design for senior roles focusing on leadership and achievements",
            "thumbnailUrl": "https://via.placeholder.com/300x400?text=Executive"
        }
    ]
    
    return {"templates": templates}

@app.post("/api/generate-with-template")
async def generate_with_template(request: TemplateRequest):
    """Generate final CV with selected template"""
    
    if request.analysis_id not in sessions:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    session_data = sessions[request.analysis_id]
    
    if "optimized_cv" not in session_data:
        raise HTTPException(status_code=400, detail="No optimized CV data found. Please generate resume first.")
    
    try:
        # Here you would integrate with your partner's template system
        # For now, we'll simulate the process
        
        cv_data = session_data["optimized_cv"]
        
        # Save data in the format expected by the template system
        template_input_file = f"template_input_{request.analysis_id}.json"
        with open(template_input_file, 'w', encoding='utf-8') as f:
            json.dump(cv_data, f, indent=2, ensure_ascii=False)
        
        # Simulate PDF generation (replace with actual template generation)
        # You would call your partner's template generation code here
        
        return {
            "status": "success",
            "message": f"CV generated with {request.template_id} template",
            "template_id": request.template_id,
            "download_url": f"/api/download-pdf/{request.analysis_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CV with template: {str(e)}")

@app.get("/api/analysis-status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis"""
    
    if analysis_id not in sessions:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    session_data = sessions[analysis_id]
    
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "has_optimized_cv": "optimized_cv" in session_data,
        "timestamp": session_data.get("timestamp", "")
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CV Optimizer API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)