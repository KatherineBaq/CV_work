import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import openai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Configuration
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# ===============================
# MODELS DE DONNÉES
# ===============================

class JobAnalysis(BaseModel):
    job_title: str
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
    company_type: str
    work_environment: List[str]
    ats_keywords: List[str]
    tone_of_voice: str
    key_responsibilities: List[str]
    company_culture_indicators: List[str]
    technical_domains: List[str]
    urgency_level: str
    remote_work_policy: str

class ProfileAnalysis(BaseModel):
    candidate_name: str
    relevance_score_overall: int
    skills_match: Dict[str, int]
    experience_relevance: List[Dict[str, Any]]
    skills_gaps: List[str]
    recommendations: List[str]
    summary: str

class GapAnalysis(BaseModel):
    overall_analysis: str
    missing_skills: List[str]

class CVSection(BaseModel):
    personal: Dict[str, str]
    education: List[Dict[str, str]]
    experience: List[Dict[str, str]]
    skills: List[str]
    links: Dict[str, str]

# ===============================
# AGENTS
# ===============================

class JobAnalyzerAgent:
    """Agent 1 : Analyse l'offre d'emploi"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    def analyze_job_offer(self, job_text: str) -> JobAnalysis:
        system_prompt = """
        You are an expert job offer analyzer for tech recruitment. Extract and structure key information from tech job offers.

        IMPORTANT: You must respond with ONLY valid JSON, no other text before or after.

        Format your response as valid JSON matching this exact schema:
        {
            "job_title": "string",
            "must_have_skills": ["array of strings"],
            "nice_to_have_skills": ["array of strings"],
            "company_type": "Unknown",
            "work_environment": ["array of strings"],
            "ats_keywords": ["array of critical keywords"],
            "tone_of_voice": "string description",
            "key_responsibilities": ["array of main duties"],
            "company_culture_indicators": ["array of culture signals"],
            "technical_domains": ["array like Frontend, Backend, DevOps, etc."],
            "urgency_level": "Normal",
            "remote_work_policy": "Unknown"
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this job offer and return JSON only:\n\n{job_text}"}
                ],
                temperature=0
            )
            
            response_content = response.choices[0].message.content
            print(f"DEBUG - Raw API response: {response_content[:500]}...")
            
            # Nettoyer la réponse (enlever markdown si présent)
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0].strip()
            
            job_data = json.loads(response_content)
            return JobAnalysis(**job_data)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw response: {response.choices[0].message.content}")
            raise Exception(f"Failed to parse job analysis JSON: {e}")
        except Exception as e:
            print(f"General error: {e}")
            raise Exception(f"Failed to analyze job offer: {e}")

class ProfileAnalyzerAgent:
    """Agent 2 : Analyse le CV contre l'offre"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    def analyze_profile(self, cv_text: str, job_analysis: JobAnalysis) -> ProfileAnalysis:
        system_prompt = """
        You are a targeted technical profile analyzer. Analyze CV against job requirements.
        
        IMPORTANT: Respond with ONLY valid JSON, no other text.
        
        JSON format required:
        {
            "candidate_name": "string",
            "relevance_score_overall": 50,
            "skills_match": {"Python": 7, "Docker": 5},
            "experience_relevance": [{"role": "string", "company": "string", "period": "string", "relevance_score": 50, "relevance_notes": "string"}],
            "skills_gaps": ["missing skills"],
            "recommendations": ["improvement suggestions"],
            "summary": "overall assessment"
        }
        """
        
        job_context = f"""
        Job Requirements:
        - Title: {job_analysis.job_title}
        - Must-have skills: {job_analysis.must_have_skills}
        - Nice-to-have skills: {job_analysis.nice_to_have_skills}
        - Key responsibilities: {job_analysis.key_responsibilities}
        - Technical domains: {job_analysis.technical_domains}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{job_context}\n\nCV Content:\n{cv_text}\n\nReturn JSON analysis only."}
                ],
                temperature=0
            )
            
            response_content = response.choices[0].message.content
            
            # Nettoyer la réponse
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0].strip()
                
            profile_data = json.loads(response_content)
            return ProfileAnalysis(**profile_data)
        except Exception as e:
            print(f"Profile analysis error: {e}")
            print(f"Raw response: {response.choices[0].message.content}")
            raise Exception(f"Failed to parse profile analysis: {e}")

class GapAnalyzerAgent:
    """Agent 3 : Détermine si on a besoin de questions utilisateur"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    def analyze_gaps(self, profile_analysis: ProfileAnalysis, threshold: int = 75) -> tuple[bool, Optional[GapAnalysis]]:
        """
        Returns (is_sufficient, gap_analysis)
        is_sufficient = True si le score est >= threshold
        
        IMPROVED: Only show gap analysis when there are significant gaps
        """
        
        # Higher threshold - only show gaps for lower scores
        score = profile_analysis.relevance_score_overall
        
        # If score is high enough, no gap analysis needed
        if score >= threshold:
            print(f"Score {score}% is sufficient (>= {threshold}%), no gap analysis needed")
            return True, None
            
        # Check if there are meaningful skills gaps to analyze
        significant_gaps = []
        
        # Analyze skills match - look for critical missing skills
        if profile_analysis.skills_match:
            low_score_skills = [skill for skill, score in profile_analysis.skills_match.items() if score <= 3]
            significant_gaps.extend(low_score_skills)
        
        # Add from existing gaps analysis
        if profile_analysis.skills_gaps:
            significant_gaps.extend(profile_analysis.skills_gaps)
        
        # If no significant gaps found, don't show gap analysis
        if len(significant_gaps) == 0 and score >= 65:
            print(f"No significant gaps found and score {score}% is reasonable, skipping gap analysis")
            return True, None
        
        # Generate gap analysis only when there are real gaps
        system_prompt = """
        You are a skills gap identifier for CV optimization. 

        Analyze the profile results and identify ONLY truly missing critical skills that would significantly improve the job match.

        IMPORTANT: 
        - Only suggest 3-5 skills maximum
        - Focus on skills that are explicitly mentioned in the job requirements but completely absent from the CV
        - Don't suggest skills the candidate already has some experience with
        - If there are no significant gaps, return an empty missing_skills array

        Return JSON format:
        {
            "overall_analysis": "Brief summary of gaps (1-2 sentences)",
            "missing_skills": ["only critical missing skills", "max 5 items"]
        }
        """
        
        context = f"""
        Profile Analysis Results:
        - Overall Score: {profile_analysis.relevance_score_overall}%
        - Skills Match: {profile_analysis.skills_match}
        - Existing Skills Gaps: {profile_analysis.skills_gaps}
        - Recommendations: {profile_analysis.recommendations}
        
        Only identify truly missing critical skills that would make a significant difference.
        If the candidate already shows good alignment, return empty missing_skills array.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.2
            )
            
            response_content = response.choices[0].message.content
            
            # Clean the response
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0].strip()
            
            gap_data = json.loads(response_content)
            
            # If no missing skills identified, don't show gap analysis
            missing_skills = gap_data.get("missing_skills", [])
            if not missing_skills or len(missing_skills) == 0:
                print("No critical missing skills identified by AI")
                return True, None
            
            # Filter out empty or very short skill names
            valid_missing_skills = [skill.strip() for skill in missing_skills if skill.strip() and len(skill.strip()) > 2]
            
            if len(valid_missing_skills) == 0:
                print("No valid missing skills after filtering")
                return True, None
            
            gap_data["missing_skills"] = valid_missing_skills
            print(f"Found {len(valid_missing_skills)} missing skills: {valid_missing_skills}")
            
            return False, GapAnalysis(**gap_data)
            
        except Exception as e:
            print(f"Gap analysis error: {e}")
            # If error in analysis, assume profile is sufficient
            return True, None

class CVGeneratorAgent:
    """Agent Final : Génère le CV optimisé"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    def generate_cv_sections(
        self, 
        job_analysis: JobAnalysis, 
        profile_analysis: ProfileAnalysis,
        user_confirmed_skills: Optional[List[str]] = None,
        requested_sections: List[str] = None
    ) -> CVSection:
        
        system_prompt = """
        You are a CV section generator. Generate optimized CV data tailored to job requirements.
        
        IMPORTANT: Respond with ONLY valid JSON matching this exact template structure:
        
        {
            "personal": {
                "name": "Full Name",
                "title": "Job Title optimized for the role",
                "email": "email@example.com",
                "phone": "+32 xxx xx xx xx",
                "location": "City, Country",
                "summary": "Professional summary optimized for the job (2-3 sentences)"
            },
            "education": [
                {
                    "degree": "Degree Name",
                    "school": "Institution Name",
                    "start": "YYYY",
                    "end": "YYYY"
                }
            ],
            "experience": [
                {
                    "title": "Optimized Job Title",
                    "company": "Company Name",
                    "start": "YYYY",
                    "end": "Present or YYYY",
                    "summary": "Optimized description with job-relevant keywords and achievements"
                }
            ],
            "skills": ["Skill1", "Skill2", "Skill3"],
            "links": {
                "linkedin": "linkedin.com/in/username",
                "github": "github.com/username"
            }
        }
        
        Instructions:
        - Use job-relevant keywords from the job analysis
        - Optimize the professional title for the target role
        - Prioritize skills that match the job requirements
        - Rewrite experience summaries to highlight relevant achievements
        - Keep the exact JSON structure shown above
        """
        
        context = f"""
        Job Analysis:
        Target Role: {job_analysis.job_title}
        Must-have skills: {job_analysis.must_have_skills}
        Nice-to-have skills: {job_analysis.nice_to_have_skills}
        Key responsibilities: {job_analysis.key_responsibilities}
        ATS Keywords: {job_analysis.ats_keywords}
        
        Candidate Profile:
        Name: {profile_analysis.candidate_name}
        Current Score: {profile_analysis.relevance_score_overall}%
        Skills Match: {profile_analysis.skills_match}
        Experience: {profile_analysis.experience_relevance}
        
        User Confirmed Skills: {user_confirmed_skills or []}
        
        Generate optimized CV data that maximizes relevance to this job offer.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{context}\n\nGenerate the optimized CV JSON:"}
                ],
                temperature=0.1
            )
            
            response_content = response.choices[0].message.content
            print(f"Raw response: {response_content[:200]}...")
            
            # Nettoyer la réponse (enlever markdown si présent)
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0].strip()
            
            cv_data = json.loads(response_content)
            return CVSection(**cv_data)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Full raw response: {response.choices[0].message.content}")
            raise Exception(f"Failed to parse CV sections JSON: {e}")
        except Exception as e:
            print(f"CV generation error: {e}")
            raise Exception(f"Failed to parse CV sections: {e}")

# ===============================
# ORCHESTRATEUR PRINCIPAL
# ===============================

class CVOptimizer:
    """Orchestrateur principal qui coordonne tous les agents"""
    
    def __init__(self):
        self.job_analyzer = JobAnalyzerAgent()
        self.profile_analyzer = ProfileAnalyzerAgent()
        self.gap_analyzer = GapAnalyzerAgent()
        self.cv_generator = CVGeneratorAgent()
        
    def optimize_cv(
        self, 
        job_offer_text: str, 
        cv_text: str,
        user_callback=None,
        requested_sections: List[str] = None
    ) -> Dict[str, Any]:
        """
        Pipeline principal d'optimisation de CV
        
        user_callback: fonction appelée si on a besoin d'input utilisateur
        Format: user_callback(gap_analysis) -> List[str] des skills confirmés
        """
        
        print("🔍 Analyzing job offer...")
        job_analysis = self.job_analyzer.analyze_job_offer(job_offer_text)
        
        print("📄 Analyzing CV profile...")
        profile_analysis = self.profile_analyzer.analyze_profile(cv_text, job_analysis)
        
        print(f"📊 Initial relevance score: {profile_analysis.relevance_score_overall}%")
        
        print("🎯 Checking if additional input needed...")
        is_sufficient, gap_analysis = self.gap_analyzer.analyze_gaps(profile_analysis)
        
        user_confirmed_skills = None
        
        if not is_sufficient and gap_analysis:
            print("❓ Additional user input required")
            print(f"Analysis: {gap_analysis.overall_analysis}")
            print(f"Missing skills: {gap_analysis.missing_skills}")
            
            if user_callback:
                user_confirmed_skills = user_callback(gap_analysis)
                print(f"✅ User confirmed skills: {user_confirmed_skills}")
            else:
                print("⚠️  No user callback provided, proceeding with current data")
        
        print("📝 Generating optimized CV sections...")
        cv_sections = self.cv_generator.generate_cv_sections(
            job_analysis,
            profile_analysis, 
            user_confirmed_skills,
            requested_sections
        )
        
        return {
            "job_analysis": job_analysis,
            "profile_analysis": profile_analysis,
            "gap_analysis": gap_analysis,
            "user_confirmed_skills": user_confirmed_skills,
            "cv_sections": cv_sections,
            "success": True
        }

# ===============================
# EXEMPLE D'UTILISATION
# ===============================

def user_input_callback(gap_analysis: GapAnalysis) -> List[str]:
    """Callback simulé pour l'input utilisateur"""
    print(f"\n=== USER INPUT REQUIRED ===")
    print(f"Analysis: {gap_analysis.overall_analysis}")
    print(f"Missing skills: {gap_analysis.missing_skills}")
    
    confirmed_skills = []
    for skill in gap_analysis.missing_skills:
        response = input(f"Do you have experience with {skill}? (y/n): ")
        if response.lower() == 'y':
            confirmed_skills.append(skill)
            
    return confirmed_skills

if __name__ == "__main__":
    # Exemple d'utilisation
    job_offer = """
    Senior Data Engineer - Microsoft Fabric Specialist
    We are seeking an experienced Data Engineer with expertise in Microsoft Fabric 
    to join our growing data team. 
    
    Requirements:
    - 5+ years experience in data engineering
    - Strong Python programming skills
    - Experience with Microsoft Fabric and Medallion Architecture
    - Knowledge of data pipelines and ETL processes
    - DevOps experience with CI/CD
    - Team mentoring and coaching abilities
    
    Nice to have:
    - Azure certifications
    - Experience with Power BI
    - Docker and containerization
    """
    
    cv_text = """
    Martin Dupont
    Développeur Full-Stack
    
    Expérience:
    TechWave Solutions – Bruxelles (Janvier 2021 – Aujourd'hui)
    - Développement d'applications Python
    - Utilisation de Docker et GitLab CI/CD
    - Mentorat de 2 développeurs juniors
    
    DigitalFactory – Bruxelles (Juillet 2018 – Décembre 2020) 
    - Développement web avec Python et JavaScript
    - Gestion de bases de données
    """
    
    # Initialiser l'optimiseur
    optimizer = CVOptimizer()
    
    # Lancer l'optimisation
    result = optimizer.optimize_cv(
        job_offer_text=job_offer,
        cv_text=cv_text,
        user_callback=user_input_callback,
        requested_sections=["professional_summary", "experience", "technical_skills"]
    )
    
    print("\n=== RESULTS ===")
    print(f"Job Title: {result['job_analysis'].job_title}")
    print(f"Initial Score: {result['profile_analysis'].relevance_score_overall}%")
    print("\n=== GENERATED CV ===")
    print(f"Name: {result['cv_sections'].personal['name']}")
    print(f"Title: {result['cv_sections'].personal['title']}")
    print(f"Summary: {result['cv_sections'].personal['summary']}")
    print(f"Experience: {result['cv_sections'].experience}")
    print(f"Skills: {result['cv_sections'].skills}")
    
    # Sauvegarder pour le système de templates
    print("\n=== SAVING FOR TEMPLATE SYSTEM ===")
    with open('optimized_input_data.json', 'w', encoding='utf-8') as f:
        json.dump(result['cv_sections'].model_dump(), f, indent=2, ensure_ascii=False)
    print("CV data saved to optimized_input_data.json")
    print("Ready to use with your partner's template system!")