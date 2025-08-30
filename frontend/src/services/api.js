import axios from 'axios';

// Replace with your actual API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Create an axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const uploadCV = async (file) => {
  const formData = new FormData();
  formData.append('cv_file', file);

  try {
    const response = await apiClient.post('/upload-cv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading CV:', error);
    throw error;
  }
};

export const analyzeJobDescription = async (cvId, jobDescription) => {
  try {
    const response = await apiClient.post('/analyze', {
      cv_id: cvId,
      job_description: jobDescription,
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing job description:', error);
    throw error;
  }
};

export const getOptimizedResume = async (analysisId) => {
  try {
    const response = await apiClient.get(`/optimized-resume/${analysisId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting optimized resume:', error);
    throw error;
  }
};

export const checkAnalysisStatus = async (analysisId) => {
  try {
    const response = await apiClient.get(`/analysis-status/${analysisId}`);
    return response.data;
  } catch (error) {
    console.error('Error checking analysis status:', error);
    throw error;
  }
};

// Helper to handle API errors
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with an error
    return {
      type: 'server',
      status: error.response.status,
      message: error.response.data.message || 'Server error occurred',
    };
  } else if (error.request) {
    // Request was made but no response received
    return {
      type: 'network',
      message: 'No response from server. Please check your internet connection.',
    };
  } else {
    // Error in setting up the request
    return {
      type: 'client',
      message: 'Error setting up the request. Please try again.',
    };
  }
};
