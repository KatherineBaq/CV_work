import React, { useState } from 'react';
import '../styles/ResultsDisplay.css';

const ResultsDisplay = ({ results }) => {
  const [activeTab, setActiveTab] = useState('recommendations');
  
  if (!results) {
    return <div>No results to display</div>;
  }

  const { matchingScore, recommendations, optimizedCV } = results;

  const downloadPDF = () => {
    // Convert base64 to blob
    const byteCharacters = atob(optimizedCV.split(',')[1]);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'application/pdf' });

    // Create download link
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'optimized_resume.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="results-display">
      <div className="score-container">
        <div className="score-circle">
          <div className="score-value">{matchingScore}%</div>
        </div>
        <div className="score-label">ATS Match Score</div>
      </div>
      
      <div className="tabs-container">
        <div className="tabs-header">
          <button 
            className={`tab-button ${activeTab === 'recommendations' ? 'active' : ''}`} 
            onClick={() => setActiveTab('recommendations')}
          >
            Recommendations
          </button>
          <button 
            className={`tab-button ${activeTab === 'preview' ? 'active' : ''}`} 
            onClick={() => setActiveTab('preview')}
          >
            Optimized CV Preview
          </button>
        </div>
        
        <div className="tab-content">
          {activeTab === 'recommendations' && (
            <div className="recommendations-tab">
              <h3>Recommended Improvements</h3>
              <ul className="recommendations-list">
                {recommendations.map((rec, index) => (
                  <li key={index} className="recommendation-item">
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {activeTab === 'preview' && (
            <div className="preview-tab">
              <div className="pdf-container">
                <iframe 
                  src={optimizedCV} 
                  title="Optimized CV Preview" 
                  className="pdf-preview"
                ></iframe>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <div className="actions-container">
        <button className="download-button" onClick={downloadPDF}>
          Download Optimized CV
        </button>
        <button className="restart-button" onClick={() => window.location.reload()}>
          Start Over
        </button>
      </div>
    </div>
  );
};

export default ResultsDisplay;
