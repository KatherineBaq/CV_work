import React, { useState } from 'react';
import CVUploader from '../components/CVUploader';
import JobDescriptionInput from '../components/JobDescriptionInput';
import ResultsDisplay from '../components/ResultsDisplay';
import '../styles/HomePage.css';

const HomePage = () => {
  const [step, setStep] = useState(1);
  const [cvFile, setCvFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCVUpload = (file) => {
    setCvFile(file);
    setStep(2);
  };

  const handleJobDescriptionSubmit = async (description) => {
    setJobDescription(description);
    setLoading(true);
    
    // TODO: Replace with actual API call
    try {
      // Simulate API call
      setTimeout(() => {
        // Mock results
        setResults({
          matchingScore: 75,
          recommendations: [
            'Add more keywords related to project management',
            'Emphasize your experience with React',
            'Include specific achievements with metrics'
          ],
          optimizedCV: 'data:application/pdf;base64,abc123...' // This would be the actual PDF data
        });
        setLoading(false);
        setStep(3);
      }, 2000);
    } catch (error) {
      console.error('Error processing resume:', error);
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return <CVUploader onUpload={handleCVUpload} />;
      case 2:
        return <JobDescriptionInput onSubmit={handleJobDescriptionSubmit} />;
      case 3:
        return <ResultsDisplay results={results} />;
      default:
        return <CVUploader onUpload={handleCVUpload} />;
    }
  };

  return (
    <div className="home-page">
      <header className="main-header">
        <div className="container">
          <h1>AI-Powered Resume Optimizer</h1>
          <p>Tailor your resume for ATS to increase your chances of getting an interview</p>
        </div>
      </header>
      
      <main className="container">
        <div className="steps-container">
          <div className={`step ${step === 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
            <span className="step-number">1</span>
            <span className="step-title">Upload CV</span>
          </div>
          <div className={`step ${step === 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-title">Job Description</span>
          </div>
          <div className={`step ${step === 3 ? 'active' : ''}`}>
            <span className="step-number">3</span>
            <span className="step-title">Results</span>
          </div>
        </div>

        <div className="content-container">
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Processing your resume...</p>
            </div>
          ) : (
            renderStep()
          )}
        </div>
      </main>
      
      <footer className="main-footer">
        <div className="container">
          <p>&copy; {new Date().getFullYear()} Resume Optimizer</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
