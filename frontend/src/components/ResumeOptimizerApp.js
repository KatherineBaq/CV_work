import React, { useState, useRef } from 'react';
import { Upload, FileText, Zap, Download, CheckCircle, AlertCircle, Clock, ArrowRight } from 'lucide-react';

// Mock API Service Module (for demonstration purposes)
// In a real app, this would connect to your backend API
const apiService = {
  uploadCV: async (file) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock successful response
    return {
      cv_id: 'mock-cv-' + Date.now(),
      message: 'CV uploaded successfully'
    };
  },

  analyzeJob: async (jobDescription, cvId) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock successful response
    return {
      analysis_id: 'mock-analysis-' + Date.now(),
      overall_match: Math.floor(60 + Math.random() * 30),  // Random score between 60-90
      skills_match: Math.floor(50 + Math.random() * 40),   // Random score between 50-90
      experience_match: Math.floor(60 + Math.random() * 35), // Random score between 60-95
      recommendations: [
        'Highlight your experience with ' + (jobDescription.includes('React') ? 'React' : 'frontend development'),
        'Add more details about your ' + (jobDescription.includes('team') ? 'team leadership' : 'project management') + ' experience',
        'Include keywords related to ' + (jobDescription.includes('agile') ? 'agile methodologies' : 'development processes')
      ],
      // New fields for missing skills
      overall_analysis: "Your profile shows strong " + 
        (jobDescription.toLowerCase().includes('react') ? 'React' : 'frontend development') + 
        " skills but lacks experience with key " + 
        (jobDescription.toLowerCase().includes('data') ? 'data platform' : 
         jobDescription.toLowerCase().includes('cloud') ? 'cloud' : 'modern framework') + 
        " technologies required for this position.",
      missing_skills: jobDescription.toLowerCase().includes('data') ? 
        ["Microsoft Fabric", "Medallion Architecture", "Azure Synapse Analytics"] :
        jobDescription.toLowerCase().includes('react') ?
          ["Next.js", "GraphQL", "React Server Components"] :
          ["CI/CD Pipeline Experience", "Docker", "Kubernetes"]
    };
  },

  generateOptimizedResume: async (analysisId, answers) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2500));
    
    // Create a simple PDF blob (in a real app, this would be an actual optimized resume)
    const pdfBlob = new Blob(['Mock optimized resume PDF content'], { type: 'application/pdf' });
    return pdfBlob;
  }
};

// Step indicator component
const StepIndicator = ({ currentStep, steps }) => (
  <div className="flex items-center justify-center mb-8">
    {steps.map((step, index) => (
      <React.Fragment key={index}>
        <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 text-sm font-semibold
          ${currentStep > index 
            ? 'bg-blue-600 border-blue-600 text-white' 
            : currentStep === index 
              ? 'border-blue-600 text-blue-600' 
              : 'border-gray-300 text-gray-400'
          }`}>
          {currentStep > index ? <CheckCircle size={20} /> : index + 1}
        </div>
        {index < steps.length - 1 && (
          <div className={`h-1 w-16 mx-2 
            ${currentStep > index ? 'bg-blue-600' : 'bg-gray-200'}`} />
        )}
      </React.Fragment>
    ))}
  </div>
);

// File upload component
const FileUpload = ({ onFileSelect, selectedFile, isUploading }) => {
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      onFileSelect(file);
    } else {
      alert('Please select a PDF file');
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div 
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${selectedFile 
            ? 'border-green-400 bg-green-50' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
          }`}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className="hidden"
          disabled={isUploading}
        />
        
        {isUploading ? (
          <div className="flex flex-col items-center">
            <Clock className="w-12 h-12 text-blue-500 animate-spin mb-4" />
            <p className="text-gray-600">Uploading your CV...</p>
          </div>
        ) : selectedFile ? (
          <div className="flex flex-col items-center">
            <CheckCircle className="w-12 h-12 text-green-500 mb-4" />
            <p className="text-green-700 font-medium">{selectedFile.name}</p>
            <p className="text-gray-500 text-sm">Click to change file</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <Upload className="w-12 h-12 text-gray-400 mb-4" />
            <p className="text-gray-600 mb-2">Upload your CV (PDF)</p>
            <p className="text-gray-400 text-sm">Click or drag to upload</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Job description input component
const JobDescriptionInput = ({ value, onChange, isAnalyzing }) => (
  <div className="w-full max-w-4xl mx-auto">
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Paste the job description here..."
      className="w-full h-64 p-4 border-2 border-gray-300 rounded-lg resize-none focus:border-blue-500 focus:outline-none"
      disabled={isAnalyzing}
    />
    {isAnalyzing && (
      <div className="flex items-center justify-center mt-4">
        <Clock className="w-5 h-5 text-blue-500 animate-spin mr-2" />
        <p className="text-blue-600">Analyzing job requirements...</p>
      </div>
    )}
  </div>
);

// Results display component
const ResultsDisplay = ({ results, onAnswerSubmit, isGenerating }) => {
  const [answers, setAnswers] = useState({});

  const handleAnswerChange = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = () => {
    onAnswerSubmit(answers);
  };

  if (!results) return null;

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Matching Metrics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
          <Zap className="w-6 h-6 text-yellow-500 mr-2" />
          Matching Analysis
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">{results.overall_match || '85'}%</div>
            <div className="text-gray-600">Overall Match</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-3xl font-bold text-green-600">{results.skills_match || '78'}%</div>
            <div className="text-gray-600">Skills Match</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-3xl font-bold text-purple-600">{results.experience_match || '92'}%</div>
            <div className="text-gray-600">Experience Match</div>
          </div>
        </div>

        {/* Key Recommendations */}
        <div className="mb-6">
          <h4 className="font-semibold text-gray-800 mb-3">Key Recommendations:</h4>
          <ul className="space-y-2">
            {(results.recommendations || [
              'Highlight your project management experience',
              'Add more specific technical skills mentioned in the job posting',
              'Emphasize your leadership and team collaboration abilities'
            ]).map((rec, index) => (
              <li key={index} className="flex items-start">
                <ArrowRight className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Missing Skills */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
          <AlertCircle className="w-6 h-6 text-amber-500 mr-2" />
          Missing Skills
        </h3>
        <p className="text-gray-600 mb-6">
          {results.overall_analysis || "Your profile shows strong experience but lacks some key skills required for this position."}
        </p>
        
        <div className="space-y-4">
          {(results.missing_skills || [
            "Microsoft Fabric",
            "Medallion Architecture"
          ]).map((skill, index) => (
            <div key={index} className="flex items-center bg-amber-50 p-4 rounded-lg border border-amber-100">
              <div className="w-2 h-2 bg-amber-500 rounded-full mr-3"></div>
              <div className="flex-grow">
                <p className="font-medium text-gray-800">{skill}</p>
              </div>
              <div>
                <input
                  type="checkbox"
                  id={`skill-${index}`}
                  checked={answers[`skill-${index}`] || false}
                  onChange={(e) => handleAnswerChange(`skill-${index}`, e.target.checked)}
                  className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={handleSubmit}
          disabled={isGenerating}
          className="mt-6 w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          {isGenerating ? (
            <>
              <Clock className="w-5 h-5 animate-spin mr-2" />
              Generating Optimized Resume...
            </>
          ) : (
            <>
              <FileText className="w-5 h-5 mr-2" />
              Generate Optimized Resume
            </>
          )}
        </button>
      </div>
    </div>
  );
};

// Success component
const SuccessScreen = ({ onDownload, onStartOver }) => (
  <div className="text-center">
    <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
      <CheckCircle className="w-12 h-12 text-green-600" />
    </div>
    
    <h2 className="text-2xl font-bold text-gray-800 mb-4">
      Your Optimized Resume is Ready!
    </h2>
    
    <p className="text-gray-600 mb-8">
      Your resume has been tailored specifically for this job posting with improved keyword matching and enhanced formatting.
    </p>
    
    <div className="space-y-4 max-w-md mx-auto">
      <button
        onClick={onDownload}
        className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center justify-center"
      >
        <Download className="w-5 h-5 mr-2" />
        Download Optimized Resume
      </button>
      
      <button
        onClick={onStartOver}
        className="w-full border border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
      >
        Optimize Another Resume
      </button>
    </div>
  </div>
);

// Template Selector Component
const TemplateSelector = ({ templates, selectedTemplate, onSelect, onSubmit, isGenerating }) => (
  <div className="max-w-4xl mx-auto">
    <h2 className="text-2xl font-bold text-gray-800 text-center mb-6">
      Choose a Resume Template
    </h2>
    
    <p className="text-gray-600 text-center mb-8">
      Select a template that best represents your professional style
    </p>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      {templates.map(template => (
        <div 
          key={template.id}
          onClick={() => onSelect(template.id)}
          className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
            selectedTemplate === template.id 
              ? 'border-blue-500 bg-blue-50 shadow-md' 
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <div className="aspect-w-4 aspect-h-3 mb-4 overflow-hidden rounded-md bg-gray-100">
            <img 
              src={template.thumbnailUrl} 
              alt={template.name} 
              className="w-full h-full object-cover"
            />
          </div>
          
          <h3 className="font-semibold text-lg mb-1">
            {template.name}
            {selectedTemplate === template.id && (
              <CheckCircle className="w-5 h-5 text-blue-500 inline ml-2" />
            )}
          </h3>
          
          <p className="text-gray-600 text-sm">
            {template.description}
          </p>
        </div>
      ))}
    </div>
    
    <div className="flex justify-center">
      <button
        onClick={onSubmit}
        disabled={isGenerating}
        className="bg-blue-600 text-white py-3 px-8 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center"
      >
        {isGenerating ? (
          <>
            <Clock className="w-5 h-5 animate-spin mr-2" />
            Generating Resume...
          </>
        ) : (
          <>
            <FileText className="w-5 h-5 mr-2" />
            Generate With This Template
          </>
        )}
      </button>
    </div>
  </div>
);

// Main App Component
const ResumeOptimizerApp = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [results, setResults] = useState(null);
  const [cvId, setCvId] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);
  const [optimizedResumeBlob, setOptimizedResumeBlob] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState('professional');
  const [availableTemplates, setAvailableTemplates] = useState([]);
  
  // Loading states
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);
  const [error, setError] = useState(null);

  const steps = ['Upload CV', 'Job Description', 'Analysis & Questions', 'Choose Template', 'Download Resume'];

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
  };

  const handleUploadCV = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    try {
      const response = await apiService.uploadCV(selectedFile);
      setCvId(response.cv_id);
      setCurrentStep(1);
    } catch (err) {
      setError('Failed to upload CV. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleJobAnalysis = async () => {
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }
    
    setIsAnalyzing(true);
    try {
      const response = await apiService.analyzeJob(jobDescription, cvId);
      setResults(response);
      setAnalysisId(response.analysis_id);
      setCurrentStep(2);
    } catch (err) {
      setError('Failed to analyze job. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnswerSubmit = async (answers) => {
    setIsLoadingTemplates(true);
    try {
      // In a real app, fetch available templates from the backend
      // Here we'll simulate it with mock data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setAvailableTemplates([
        {
          id: 'professional',
          name: 'Professional',
          description: 'A clean, professional template with a traditional layout',
          thumbnailUrl: 'https://via.placeholder.com/150?text=Professional'
        },
        {
          id: 'modern',
          name: 'Modern',
          description: 'A contemporary design with bold elements and creative layout',
          thumbnailUrl: 'https://via.placeholder.com/150?text=Modern'
        },
        {
          id: 'technical',
          name: 'Technical',
          description: 'Optimized for technical roles with focus on skills and projects',
          thumbnailUrl: 'https://via.placeholder.com/150?text=Technical'
        },
        {
          id: 'executive',
          name: 'Executive',
          description: 'Elegant design for senior roles focusing on leadership and achievements',
          thumbnailUrl: 'https://via.placeholder.com/150?text=Executive'
        }
      ]);
      
      // Move to template selection step
      setCurrentStep(3);
    } catch (err) {
      setError('Failed to load resume templates. Please try again.');
    } finally {
      setIsLoadingTemplates(false);
    }
  };
  
  const handleTemplateSelect = (templateId) => {
    setSelectedTemplate(templateId);
  };
  
  const handleGenerateResume = async () => {
    setIsGenerating(true);
    try {
      // In a real app, pass the selected template to the backend
      const resumeBlob = await apiService.generateOptimizedResume(analysisId, {
        template: selectedTemplate,
        // Include other data that might be needed
        // ...other parameters
      });
      setOptimizedResumeBlob(resumeBlob);
      setCurrentStep(4);
    } catch (err) {
      setError('Failed to generate resume. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (optimizedResumeBlob) {
      const url = URL.createObjectURL(optimizedResumeBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'optimized_resume.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleStartOver = () => {
    setCurrentStep(0);
    setSelectedFile(null);
    setJobDescription('');
    setResults(null);
    setCvId(null);
    setAnalysisId(null);
    setOptimizedResumeBlob(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-800 text-center">
            AI-Powered Resume Optimizer
          </h1>
          <p className="text-gray-600 text-center mt-2">
            Tailor your resume for any job posting with AI-powered optimization
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <StepIndicator currentStep={currentStep} steps={steps} />
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-8">
          {currentStep === 0 && (
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Upload Your Current Resume</h2>
              <FileUpload 
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
                isUploading={isUploading}
              />
              {selectedFile && (
                <button
                  onClick={handleUploadCV}
                  disabled={isUploading}
                  className="mt-6 bg-blue-600 text-white py-3 px-8 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  Continue to Next Step
                </button>
              )}
            </div>
          )}

          {currentStep === 1 && (
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Enter Job Description</h2>
              <JobDescriptionInput 
                value={jobDescription}
                onChange={setJobDescription}
                isAnalyzing={isAnalyzing}
              />
              {jobDescription && (
                <button
                  onClick={handleJobAnalysis}
                  disabled={isAnalyzing}
                  className="mt-6 bg-blue-600 text-white py-3 px-8 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  Analyze Job Match
                </button>
              )}
            </div>
          )}

          {currentStep === 2 && (
            <ResultsDisplay 
              results={results}
              onAnswerSubmit={handleAnswerSubmit}
              isGenerating={isGenerating}
            />
          )}

          {currentStep === 3 && (
            <TemplateSelector 
              templates={availableTemplates}
              selectedTemplate={selectedTemplate}
              onSelect={handleTemplateSelect}
              onSubmit={handleGenerateResume}
              isGenerating={isGenerating}
            />
          )}
          
          {currentStep === 4 && (
            <SuccessScreen 
              onDownload={handleDownload}
              onStartOver={handleStartOver}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6 text-center text-gray-500">
          <p>&copy; {new Date().getFullYear()} AI Resume Optimizer. Built with React and powered by AI.</p>
        </div>
      </footer>
    </div>
  );
};

export default ResumeOptimizerApp;
