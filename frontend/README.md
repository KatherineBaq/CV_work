# Resume Optimizer Frontend

This is the frontend for the AI-Powered Resume Optimizer application, a tool designed to tailor resumes for specific job offers to increase chances of passing through Applicant Tracking Systems (ATS).

## Features

- **Modern UI**: Clean, responsive design using TailwindCSS and React
- **Step-by-Step Flow**: Guided user experience from upload to download
- **Interactive Components**: Dynamic file upload, job description analysis, and results display
- **Backend Integration**: Ready-to-use API service for connecting with the backend

## Tech Stack

- **React**: Frontend library for building the user interface
- **TailwindCSS**: Utility-first CSS framework for styling
- **Lucide React**: Icon library for enhanced UI

## Getting Started

### Prerequisites

- Node.js (v14 or newer)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will open in your browser at http://localhost:3000.

## API Integration

The application is pre-configured to connect with the backend API. The endpoints are defined in the `apiService` object in the `ResumeOptimizerApp.js` file. Update the `API_BASE_URL` constant to match your backend URL.

## Project Structure

- `src/components/ResumeOptimizerApp.js`: Main application component
- `src/components/`: Reusable UI components
- `src/styles/`: CSS files for styling
- `public/`: Static assets

## Next Steps

1. Customize the UI to match your brand identity
2. Connect with your backend team to finalize API integration
3. Add additional features like user authentication, saved resumes, etc.
