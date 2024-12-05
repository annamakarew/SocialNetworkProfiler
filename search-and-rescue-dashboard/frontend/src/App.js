import React, { useState } from 'react';
import axios from 'axios';
import SentimentAnalysis from './components/SentimentAnalysis';
import ObjectRecognition from './components/ObjectRecognition';
import './App.css';

const App = () => {
  const [username, setUsername] = useState('');
  const [sentimentData, setSentimentData] = useState(null);
  const [objectRecognitionData, setObjectRecognitionData] = useState(null);
  // State to store the data from the response
  const [responseData, setResponseData] = useState(null); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [spreadsheetData, setSpreadsheetData] = useState(null);
  const [displayTime, setDisplayTime] = useState(null); // New state for display time

  const handleSearch = async () => {
    // Check if the username is empty
    if (!username.trim()) {
      alert('Please enter a valid Instagram username.');
      return;
    }

    setLoading(true);
    setError(null);
    setSpreadsheetData(null); // Clear previous data

    try {
      // Send a POST request to the backend with the username
      const response = await axios.post('http://localhost:5001/api/fetch-data', {
          username,
      });
  
      // Set the returned spreadsheet data
      setSpreadsheetData(response.data);

      // Measure the time to display the results
      const displayStartTime = performance.now();
      setTimeout(() => {
        const displayEndTime = performance.now();
        const timeTaken = (displayEndTime - displayStartTime) / 1000; // Convert to seconds
        setDisplayTime(timeTaken);

        // Log the display time (you can also save this to a server if needed)
        console.log(`Time taken to display results: ${timeTaken.toFixed(2)} seconds`);
      }, 0); // Ensure this happens right after rendering
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Social Network Profiler Dashboard</h1>
        <p>Analyze Instagram captions for sentiment, named entities, and object recognition.</p>
      </header>
      <main>
        <div className="search-section">
          <input
            type="text"
            className="input-box"
            placeholder="Enter Instagram username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <button className="search-button" onClick={handleSearch}>
            Search
          </button>
        </div>

        {loading && <p className="loading-text">Loading...</p>}
        {error && <p className="error-text">{error}</p>}

        {spreadsheetData && (
          <div className="results-section">
            <div className="table-container">
              <table className="results-table">
              <thead>
                <tr>
                  <th>Caption</th>
                  <th>Sentiment</th>
                  <th>Named Entities</th>
                  <th>Generated Caption</th>
                  <th>Image</th>
                  <th>Objects Detected</th>
                </tr>
              </thead>

                <tbody>
                  {spreadsheetData.map((row, index) => (
                    <tr key={index}>
                      <td>{row.Caption}</td>
                      <td>{row.Sentiment}</td>
                      <td>{row["Named Entities"]}</td>
                      <td>{row["Generated Caption"]}</td>
                      <td style={{width: "25%"}}>
                        <img
                          src={row.Image}
                          alt="Detected objects"
                          style={{ width: "100%", maxWidth: "9000px", border: "1px solid #ccc" }}
                        />
                      </td>
                      <td style={{ verticalAlign: "top", paddingLeft: "15px", width: "15%", fontSize: "12px"}}>
                        <ul style={{ listStyleType: "disc", margin: "0", padding: "0" }}>
                          {row["Objects Detected"] && Array.isArray(row["Objects Detected"]) ? (
                            row["Objects Detected"].map((obj, objIndex) => (
                              <div key={objIndex}>
                                <strong>{obj.label}</strong>: {obj.coordinates.join(", ")}
                              </div>
                            ))
                          ) : (
                            <li>No objects detected</li>
                          )}
                        </ul>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
      <footer className="footer">
        <p>© 2024 Social Network Profiler. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;
