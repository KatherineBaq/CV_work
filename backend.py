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
import PyPDF2
import io
import traceback
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

def cleanup_temp_files(file_paths: List[str]):
    """Clean up temporary files after processing"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Failed to clean up {file_path}: {e}")

def generate_cv_with_template(cv_data: Dict, template_id: str, analysis_id: str) -> str:
    """Generate CV using the template system and return PDF path"""
    
    logger.info(f"Starting CV generation with template_id: {template_id}, analysis_id: {analysis_id}")
    logger.info(f"CV data keys: {list(cv_data.keys())}")
    
    # Template mapping - FIXED: Added full path
    template_mapping = {
        'template1': 'create_cv/template1.docx',  # Added create_cv/ prefix
        'template2': 'create_cv/template2.docx'   # Added create_cv/ prefix
    }
    
    template_file = template_mapping.get(template_id, 'create_cv/template1.docx')
    logger.info(f"Using template file: {template_file}")
    
    # Create file names with full paths
    json_file = f"temp_cv_data_{analysis_id}.json"
    output_docx = f"temp_output_{analysis_id}.docx"
    output_pdf = f"temp_output_{analysis_id}.pdf"
    
    try:
        # Check if template exists BEFORE importing
        if not Path(template_file).exists():
            logger.error(f"Template file not found: {template_file}")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"Files in create_cv/: {list(Path('create_cv').glob('*')) if Path('create_cv').exists() else 'create_cv directory not found'}")
            raise Exception(f"Template {template_file} not found. Please ensure template files are in the create_cv/ directory")
        
        # Import the CV generation functions AFTER checking template exists
        try:
            from create_cv.python_cv_templates import render_template, convert_to_pdf
            logger.info("Successfully imported CV template functions")
        except ImportError as e:
            logger.error(f"Import error: {e}")
            logger.info(f"Python path: {os.sys.path}")
            logger.info(f"Current directory contents: {os.listdir('.')}")
            raise Exception(f"CV template functions not found. Error: {str(e)}. Make sure python_cv_templates.py is in create_cv/ folder and dependencies are installed.")
        
        # Save CV data to JSON file
        logger.info(f"Saving CV data to {json_file}")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cv_data, f, indent=2, ensure_ascii=False)
        logger.info("CV data saved successfully")
        
        # Generate CV using your functions
        logger.info("Rendering template...")
        render_template(template_file, cv_data, output_docx)
        logger.info(f"Template rendered to {output_docx}")
        
        # Check if DOCX was created
        if not os.path.exists(output_docx):
            raise Exception(f"DOCX file was not created: {output_docx}")
        
        logger.info("Converting to PDF...")
        convert_to_pdf(output_docx, output_pdf)
        logger.info(f"PDF created: {output_pdf}")
        
        # Verify PDF was created
        if not os.path.exists(output_pdf):
            raise Exception(f"PDF generation failed - file not found: {output_pdf}")
        
        # Check PDF file size
        pdf_size = os.path.getsize(output_pdf)
        logger.info(f"Generated PDF size: {pdf_size} bytes")
        
        if pdf_size == 0:
            raise Exception("PDF file is empty")
        
        # Clean up intermediate files
        cleanup_temp_files([json_file])  # Keep DOCX for debugging, only clean JSON
        
        logger.info(f"CV generation completed successfully: {output_pdf}")
        return output_pdf
        
    except Exception as e:
        logger.error(f"Error in CV generation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Clean up files in case of error
        cleanup_temp_files([json_file, output_docx, output_pdf])
        raise Exception(f"Failed to generate CV: {str(e)}")

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
        logger.info("Step 1: Analyzing job offer...")
        job_analysis = optimizer.job_analyzer.analyze_job_offer(request.job_description)
        logger.info(f"Job analysis completed for role: {job_analysis.job_title}")
        
        # Step 2: Analyze profile
        logger.info("Step 2: Analyzing profile against job...")
        profile_analysis = optimizer.profile_analyzer.analyze_profile(cv_text, job_analysis)
        logger.info(f"Profile analysis completed - Score: {profile_analysis.relevance_score_overall}%")
        
        # Step 3: Check if additional input needed (IMPROVED LOGIC)
        logger.info("Step 3: Analyzing gaps...")
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
        
        # Calculate more realistic scores
        overall_score = profile_analysis.relevance_score_overall
        skills_score = max(profile_analysis.skills_match.values()) if profile_analysis.skills_match else max(50, overall_score - 10)
        experience_score = min(overall_score + 10, 95)  # Experience usually scores higher
        
        # Prepare base response
        response_data = {
            "analysis_id": analysis_id,
            "overall_match": overall_score,
            "skills_match": skills_score,
            "experience_match": experience_score,
            "recommendations": profile_analysis.recommendations[:4] if profile_analysis.recommendations else []
        }
        
        # IMPROVED: Only add gap analysis if there are real gaps AND not sufficient
        if not is_sufficient and gap_analysis and gap_analysis.missing_skills:
            logger.info(f"Gap analysis needed - Missing skills: {gap_analysis.missing_skills}")
            response_data.update({
                "overall_analysis": gap_analysis.overall_analysis,
                "missing_skills": gap_analysis.missing_skills,
                "needs_user_input": True
            })
        else:
            logger.info(f"No gap analysis needed - Score: {overall_score}%, is_sufficient: {is_sufficient}")
            response_data["needs_user_input"] = False
        
        logger.info(f"Returning response - needs_user_input: {response_data.get('needs_user_input', False)}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error in analyze_job_description: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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
        
        # Store for template generation
        sessions[request.analysis_id]["optimized_cv"] = optimized_cv_data
        
        return {
            "status": "success",
            "message": "Optimized CV data generated successfully",
            "cv_data": optimized_cv_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CV: {str(e)}")

@app.post("/api/generate-final-cv")
async def generate_final_cv(request: TemplateRequest, background_tasks: BackgroundTasks):
    """Generate final CV with selected template"""
    
    logger.info(f"Received final CV generation request for analysis_id: {request.analysis_id}, template_id: {request.template_id}")
    
    if request.analysis_id not in sessions:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    session_data = sessions[request.analysis_id]
    
    if "optimized_cv" not in session_data:
        raise HTTPException(status_code=400, detail="No optimized CV data found. Please generate resume first.")
    
    try:
        cv_data = session_data["optimized_cv"]
        logger.info(f"Retrieved CV data with keys: {list(cv_data.keys())}")
        
        # Generate PDF using template system
        pdf_path = generate_cv_with_template(cv_data, request.template_id, request.analysis_id)
        logger.info(f"PDF generated successfully at: {pdf_path}")
        
        # Verify PDF was created and is accessible
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="PDF file was not created")
        
        # Check file permissions
        if not os.access(pdf_path, os.R_OK):
            raise HTTPException(status_code=500, detail="Cannot read generated PDF file")
        
        # Schedule cleanup of temporary files after response is sent
        temp_files = [pdf_path]  # Only cleanup PDF after sending
        background_tasks.add_task(cleanup_temp_files, temp_files)
        
        # Return PDF file
        return FileResponse(
            path=pdf_path,
            filename=f"optimized_cv_{request.template_id}.pdf",
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=optimized_cv_{request.template_id}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in generate_final_cv: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate final CV: {str(e)}")

# Add a debug endpoint to check template files
@app.get("/api/debug/templates")
async def debug_templates():
    """Debug endpoint to check template files"""
    try:
        current_dir = os.getcwd()
        create_cv_exists = Path("create_cv").exists()
        create_cv_files = list(Path("create_cv").glob("*")) if create_cv_exists else []
        
        template_files = {
            "template1.docx": Path("create_cv/template1.docx").exists(),
            "template2.docx": Path("create_cv/template2.docx").exists(),
        }
        
        return {
            "current_directory": current_dir,
            "create_cv_directory_exists": create_cv_exists,
            "create_cv_files": [str(f) for f in create_cv_files],
            "template_files": template_files,
            "python_path": os.sys.path
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/download/{analysis_id}")
async def download_optimized_cv(analysis_id: str):
    """Download the optimized CV JSON file"""
    
    if analysis_id not in sessions:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    session_data = sessions[analysis_id]
    
    if "optimized_cv" not in session_data:
        raise HTTPException(status_code=404, detail="No optimized CV data found")
    
    # Create temporary JSON file
    json_file = f"download_cv_{analysis_id}.json"
    
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(session_data["optimized_cv"], f, indent=2, ensure_ascii=False)
        
        return FileResponse(
            path=json_file,
            filename=f"optimized_cv_{analysis_id}.json",
            media_type="application/json"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create download file: {str(e)}")
    
    finally:
        # Clean up the temporary file after a delay
        if os.path.exists(json_file):
            os.remove(json_file)

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

@app.get("/api/template-preview/{template_id}")
async def get_template_preview(template_id: str):
    image_mapping = {
        'template1': 'cv1.png',
        'template2': 'cv2.png'
    }
    
    image_file = image_mapping.get(template_id)
    if not image_file:
        raise HTTPException(status_code=404, detail="Template preview not found")
    
    # Check multiple possible paths for the image
    possible_paths = [
        Path(f"frontend/public/template/{image_file}"),
        Path(f"template/{image_file}"),
        Path(f"static/template/{image_file}"),
        Path(f"public/template/{image_file}")
    ]
    
    image_path = None
    for path in possible_paths:
        if path.exists():
            image_path = path
            break
    
    if not image_path:
        raise HTTPException(status_code=404, detail=f"Preview image not found. Searched: {[str(p) for p in possible_paths]}")
    
    return FileResponse(path=str(image_path), media_type="image/png")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CV Optimizer API"}

if __name__ == "__main__":
    import uvicorn
    import sys
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)