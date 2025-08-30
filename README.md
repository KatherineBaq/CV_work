Project Name: AI-Powered Resume Optimizer

🚀 Project Goal
Our goal is to build an MVP for an AI-powered tool that tailors a user's resume for a specific job offer. The system will leverage a multi-agent architecture to parse job descriptions, analyze a user's professional profile, and generate a highly-optimized, ATS-friendly resume. The MVP will focus on a core, functional workflow: Job Offer Parsing → User Profile Matching → Optimized Resume Generation.

💻 Tech Stack

Backend

Language: Python 🐍

Frontend

Framework: React

API Calls: Axios or the native fetch API

💡 MVP Workflow
The MVP will implement a simplified version of our multi-agent model.

User Input: The user paste a job description in text box 

User Input: The user uploads CV in PDF.

Backend Processing:

Agent 1 (Offre) → Agent 2 (Profil) → Agent 3 (Match) 
                                        ↓
Agent 4 (Recommandations) ← User Input ← Questions ciblées
                ↓
Agent 5 (Génération CV optimisé)

Frontend Display: Matching Mertics & Recommendations

Frontend Display: The generated resume is presented to the user for download as a PDF.


🧑‍💻 Team Responsibilities

Developer 1:

Build the core API endpoints using FastAPI.

Implement Agent 1 (Offer Parser) for job description analysis.

Set up the PostgreSQL database schema and user profile data models.

Developer 2:

Implement Agent 2 (Profile Matcher) to compare job data with the user's profile.

Develop Agent 3 (Generator) for creating the final resume document.

Set up the Celery/Redis background task system for efficient processing.

Frontend Developer (1)

Build the single-page application using React/Vue.js.

Design and implement the user interface for inputting job descriptions and profile data.

Integrate the frontend with the backend API to send data and receive the generated resume.

Ensure the UI is clean, intuitive, and mobile-responsive.

🛠️ Getting Started

