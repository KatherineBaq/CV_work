import React, { useState } from 'react';
import '../styles/CVUploader.css';

const CVUploader = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    validateAndSetFile(selectedFile);
  };

  const validateAndSetFile = (selectedFile) => {
    setError('');
    
    if (!selectedFile) {
      return;
    }
    
    if (selectedFile.type !== 'application/pdf') {
      setError('Please upload a PDF file only');
      return;
    }
    
    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File size should be less than 5MB');
      return;
    }
    
    setFile(selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    validateAndSetFile(droppedFile);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please upload your CV');
      return;
    }
    
    onUpload(file);
  };

  return (
    <div className="cv-uploader">
      <h2>Upload Your CV</h2>
      <p>Upload your current resume in PDF format</p>
      
      <form onSubmit={handleSubmit}>
        <div 
          className={`drop-area ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input 
            type="file" 
            id="cv-file" 
            accept=".pdf" 
            onChange={handleFileChange}
            className="file-input"
          />
          <label htmlFor="cv-file" className="file-label">
            {file ? (
              <>
                <span className="file-name">{file.name}</span>
                <span className="change-file">Change file</span>
              </>
            ) : (
              <>
                <span className="upload-icon">📄</span>
                <span className="upload-text">
                  Drag & drop your CV here or <span className="browse">browse</span>
                </span>
                <span className="file-hint">PDF format only, max 5MB</span>
              </>
            )}
          </label>
        </div>
        
        {error && <p className="error-message">{error}</p>}
        
        <button 
          type="submit" 
          className="primary-button"
          disabled={!file}
        >
          Continue
        </button>
      </form>
    </div>
  );
};

export default CVUploader;
