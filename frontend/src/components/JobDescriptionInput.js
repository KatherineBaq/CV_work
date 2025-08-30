import React, { useState } from 'react';
import '../styles/JobDescriptionInput.css';

const JobDescriptionInput = ({ onSubmit }) => {
  const [jobDescription, setJobDescription] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!jobDescription.trim() || jobDescription.length < 50) {
      setError('Please enter a detailed job description (at least 50 characters)');
      return;
    }
    
    onSubmit(jobDescription);
  };

  return (
    <div className="job-description-input">
      <h2>Enter Job Description</h2>
      <p>Paste the job description you want to optimize your resume for</p>
      
      <form onSubmit={handleSubmit}>
        <textarea
          value={jobDescription}
          onChange={(e) => {
            setJobDescription(e.target.value);
            setError('');
          }}
          placeholder="Paste job description here..."
          rows={10}
          className="job-description-textarea"
        ></textarea>
        
        {error && <p className="error-message">{error}</p>}
        
        <div className="character-count">
          {jobDescription.length} characters
        </div>
        
        <div className="buttons-container">
          <button type="button" className="secondary-button" onClick={() => window.history.back()}>
            Back
          </button>
          <button type="submit" className="primary-button">
            Analyze and Optimize
          </button>
        </div>
      </form>
    </div>
  );
};

export default JobDescriptionInput;
