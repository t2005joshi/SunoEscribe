import { useState } from "react";
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [transcription, setTranscription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detectedLanguage, setDetectedLanguage] = useState("");
  const [languageName, setLanguageName] = useState("");
  const [processingStage, setProcessingStage] = useState("");
  const [showLanguageDetection, setShowLanguageDetection] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setTranscription("");
    setError("");
    setDetectedLanguage("");
    setLanguageName("");
    setProcessingStage("");
    setShowLanguageDetection(false);
    
    // Validate file type
    if (selectedFile && !selectedFile.type.startsWith('audio/')) {
      setError("Please select a valid audio file (MP3, WAV, etc.)");
      setFile(null);
      return;
    }
    
    // Validate file size (50MB limit)
    if (selectedFile && selectedFile.size > 50 * 1024 * 1024) {
      setError("File size must be less than 50MB");
      setFile(null);
      return;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError("Please select an audio file.");
      return;
    }
    
    setLoading(true);
    setTranscription("");
    setError("");
    setDetectedLanguage("");
    setLanguageName("");
    setShowLanguageDetection(false);
    setProcessingStage("Uploading and isolating vocals...");
    
    const formData = new FormData();
    formData.append("audio", file);

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      console.log("Making request to:", `${apiUrl}/api/transcribe`);
      
      setProcessingStage("Processing audio file...");
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout
      
      const response = await fetch(`${apiUrl}/api/transcribe`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
        headers: {
          // Remove Content-Type header to let browser set it with boundary
        },
      });
      
      clearTimeout(timeoutId);
      
      console.log("Response status:", response.status);
      console.log("Response headers:", [...response.headers.entries()]);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        throw new Error(`Server error (${response.status}): ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log("Response data:", data);
      
      if (data.error) {
        setError(data.error);
        return;
      }
      
      // Show language detection if available
      if (data.language && data.language_name) {
        setDetectedLanguage(data.language);
        setLanguageName(data.language_name);
        setShowLanguageDetection(true);
        setProcessingStage("Transcribing audio...");
        
        // Brief delay to show language detection
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
      
      setTranscription(data.transcription || "No transcription found.");
      
    } catch (err) {
      console.error("Fetch error:", err);
      
      if (err.name === 'AbortError') {
        setError("Request timeout. Please try with a shorter audio file.");
      } else if (err.message.includes('Failed to fetch')) {
        setError("Cannot connect to server. Please check if the backend is running on the correct port.");
      } else {
        setError(`Connection error: ${err.message}`);
      }
    } finally {
      setLoading(false);
      setProcessingStage("");
    }
  };

  return (
    <div className="app-container">
      {/* Animated background elements */}
      <div className="background-overlay">
        <div className="floating-circle circle1"></div>
        <div className="floating-circle circle2"></div>
        <div className="floating-circle circle3"></div>
      </div>

      <div className="main-content">
        {/* Header */}
        <div className="header">
          <div className="title-container">
            <div className="logo-container">
              <img 
                src="/logo.png"
                alt="SunoEscribe Logo"
                className="logo"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="logo-fallback" style={{display: 'none'}}>🎵</div>
            </div>
            <div className="title-text">
              <h1 className="title">SunoEscribe</h1>
              <p className="subtitle">AI-Powered Audio Transcription</p>
            </div>
          </div>
        </div>

        {/* Main Card */}
        <div className="main-card">
          {/* Rainbow bar */}
          <div className="rainbow-bar"></div>
          
          <div className="card-content">
            <div className="description">
              <div className="description-content">
                <div className="music-icon">🎵</div>
                <div>
                  <p className="description-text">
                    Upload a song or audio file and get the lyrics transcribed in any supported language!
                  </p>
                  <p className="limit-text">
                    (Only the first 30 seconds will be transcribed)
                  </p>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="form-container">
              <div className="input-container">
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileChange}
                  className="file-input"
                  disabled={loading}
                />
                <div className="input-label">
                  <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  {file ? file.name : "Choose audio file"}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || !file}
                className={`submit-button ${loading ? 'disabled' : 'enabled'}`}
              >
                {loading ? (
                  <div className="loading-container">
                    <div className="spinner"></div>
                    <span>Transcribing...</span>
                  </div>
                ) : (
                  <div className="button-content">
                    <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    <span>Transcribe Audio</span>
                  </div>
                )}
              </button>
            </form>

            {/* Processing Stage */}
            {processingStage && (
              <div className="processing-stage">
                <div className="processing-content">
                  <div className="processing-spinner"></div>
                  <span className="processing-text">{processingStage}</span>
                </div>
              </div>
            )}

            {/* Language Detection */}
            {showLanguageDetection && detectedLanguage && (
              <div className="language-detection">
                <div className="language-content">
                  <div className="language-icon">
                    <svg className="language-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                    </svg>
                  </div>
                  <div className="language-text-container">
                    <span className="language-label">Language Detected: </span>
                    <span className="language-value">{languageName}</span>
                    <span className="language-code">({detectedLanguage})</span>
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="error-message">
                <div className="error-content">
                  <div className="error-icon">
                    <svg className="error-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <span className="error-text">{error}</span>
                </div>
              </div>
            )}

            {/* Transcription Results */}
            {transcription && (
              <div className="transcription-results">
                <div className="transcription-header">
                  <div className="transcription-icon">
                    <svg className="transcription-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h2 className="transcription-title">Transcription Results</h2>
                </div>
                <div className="transcription-content">
                  <pre className="transcription-text">{transcription}</pre>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="footer">
          <p className="footer-text">Made with ❤️ for music lovers</p>
        </div>
      </div>
    </div>
  );
}

export default App;