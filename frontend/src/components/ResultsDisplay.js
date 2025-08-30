import React, { useState } from 'react';
import { Zap, AlertCircle, ArrowRight, CheckCircle, Clock, FileText, Award, TrendingUp } from 'lucide-react';

const ResultsDisplay = ({ results, onAnswerSubmit, isGenerating }) => {
  const [answers, setAnswers] = useState({});

  const handleAnswerChange = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = () => {
    // Convert checkbox answers to confirmed skills array
    const confirmedSkills = Object.keys(answers)
      .filter(key => answers[key] === true)
      .map(key => {
        const index = parseInt(key.split('-')[1]);
        return (results.missing_skills || [])[index];
      })
      .filter(skill => skill);

    console.log('Confirmed skills:', confirmedSkills);
    onAnswerSubmit(confirmedSkills);
  };

  if (!results) {
    return (
      <div className="flex items-center justify-center p-8">
        <Clock className="w-8 h-8 text-blue-500 animate-spin mr-3" />
        <span className="text-gray-600">Analyzing your profile...</span>
      </div>
    );
  }

  // Debug: Log what we received
  console.log('Results received:', results);
  console.log('Missing skills:', results.missing_skills);
  console.log('Needs user input:', results.needs_user_input);

  // IMPROVED: More strict check for missing skills
  const hasMissingSkills = results.missing_skills && 
                          results.missing_skills.length > 0 && 
                          results.needs_user_input === true;

  const isHighScore = results.overall_match >= 75;

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Matching Metrics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <Zap className="w-6 h-6 text-yellow-500 mr-2" />
          Profile Analysis Results
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className={`text-center p-6 rounded-lg ${
            results.overall_match >= 80 ? 'bg-green-50 border-2 border-green-200' :
            results.overall_match >= 60 ? 'bg-blue-50 border-2 border-blue-200' :
            'bg-orange-50 border-2 border-orange-200'
          }`}>
            <div className={`text-4xl font-bold mb-2 ${
              results.overall_match >= 80 ? 'text-green-600' :
              results.overall_match >= 60 ? 'text-blue-600' :
              'text-orange-600'
            }`}>
              {results.overall_match || 75}%
            </div>
            <div className="text-gray-600 font-medium">Overall Match</div>
            {results.overall_match >= 80 && (
              <div className="flex items-center justify-center mt-2">
                <Award className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-600 text-sm font-medium">Excellent</span>
              </div>
            )}
          </div>
          
          <div className="text-center p-6 bg-green-50 rounded-lg border-2 border-green-200">
            <div className="text-4xl font-bold text-green-600 mb-2">{results.skills_match || 68}%</div>
            <div className="text-gray-600 font-medium">Skills Match</div>
            <div className="flex items-center justify-center mt-2">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600 text-sm font-medium">Good alignment</span>
            </div>
          </div>
          
          <div className="text-center p-6 bg-purple-50 rounded-lg border-2 border-purple-200">
            <div className="text-4xl font-bold text-purple-600 mb-2">{results.experience_match || 82}%</div>
            <div className="text-gray-600 font-medium">Experience Match</div>
            <div className="flex items-center justify-center mt-2">
              <CheckCircle className="w-4 h-4 text-purple-500 mr-1" />
              <span className="text-purple-600 text-sm font-medium">Strong fit</span>
            </div>
          </div>
        </div>

        {/* Key Recommendations */}
        {results.recommendations && results.recommendations.length > 0 && (
          <div className="bg-gray-50 rounded-lg p-5">
            <h4 className="font-bold text-gray-800 mb-3 flex items-center">
              <ArrowRight className="w-5 h-5 text-blue-500 mr-2" />
              Optimization Recommendations
            </h4>
            <ul className="space-y-2">
              {results.recommendations.slice(0, 4).map((rec, index) => (
                <li key={index} className="flex items-start">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-gray-700 text-sm leading-relaxed">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* CONDITIONAL: Missing Skills Section - Only show if there are actual gaps */}
      {hasMissingSkills ? (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <AlertCircle className="w-6 h-6 text-amber-500 mr-2" />
            Skills Enhancement Opportunities
          </h3>
          
          <div className="mb-6 p-4 bg-amber-50 rounded-lg border-l-4 border-amber-400">
            <p className="text-gray-700 leading-relaxed">
              {results.overall_analysis || 
               "We've identified some additional skills that could strengthen your profile for this position. Please let us know which of these you have experience with."}
            </p>
          </div>
          
          <div className="space-y-3">
            <p className="font-medium text-gray-800 mb-4">
              Select any skills you have experience with:
            </p>
            
            {results.missing_skills.map((skill, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-50 p-4 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-amber-400 rounded-full mr-3"></div>
                  <div>
                    <p className="font-medium text-gray-800">{skill}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <label htmlFor={`skill-${index}`} className="text-sm text-gray-600 cursor-pointer">
                    I have this skill
                  </label>
                  <input
                    type="checkbox"
                    id={`skill-${index}`}
                    checked={answers[`skill-${index}`] || false}
                    onChange={(e) => handleAnswerChange(`skill-${index}`, e.target.checked)}
                    className="w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer"
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-700">
              <strong>Tip:</strong> Even if these skills aren't prominent in your current CV, selecting them will help us optimize your resume to better highlight your capabilities.
            </p>
          </div>

          <button
            onClick={handleSubmit}
            disabled={isGenerating}
            className="mt-6 w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {isGenerating ? (
              <>
                <Clock className="w-5 h-5 animate-spin mr-2" />
                Generating Optimized Resume Data...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5 mr-2" />
                Continue to Template Selection
              </>
            )}
          </button>
        </div>
      ) : (
        /* HIGH SCORE: No missing skills section, direct continue */
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          
          <h3 className="text-2xl font-bold text-gray-800 mb-3">
            {isHighScore ? 'Excellent Match!' : 'Good Profile Match!'}
          </h3>
          
          <p className="text-gray-600 mb-6 max-w-md mx-auto leading-relaxed">
            {isHighScore 
              ? "Your profile shows excellent alignment with this job posting. Your experience and skills are well-matched for this role."
              : "Your profile shows good alignment with this job posting. Let's create an optimized resume that highlights your strengths."
            }
          </p>
          
          <div className="bg-green-50 rounded-lg p-4 mb-6 inline-block">
            <p className="text-green-700 text-sm">
              <strong>Ready to proceed:</strong> No additional information needed
            </p>
          </div>
          
          <button
            onClick={() => handleSubmit()}
            disabled={isGenerating}
            className="bg-green-600 text-white py-3 px-8 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center justify-center mx-auto shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            {isGenerating ? (
              <>
                <Clock className="w-5 h-5 animate-spin mr-2" />
                Generating...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5 mr-2" />
                Continue to Template Selection
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;