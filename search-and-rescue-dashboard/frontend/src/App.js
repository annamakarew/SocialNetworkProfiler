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

  const handleSearch = async () => {
    // Check if the username is empty
    if (!username.trim()) {
      alert('Please enter a valid Instagram username.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Send a POST request to the backend with the username
      const response = await axios.post('http://localhost:5001/api/fetch-data', {
          username,
      });
  
      // Set the returned spreadsheet data
      setSpreadsheetData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Social Network Profiler Dashboard</h1>
      <div className="input-section">
        <input
          type="text"
          placeholder="Enter Instagram username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {spreadsheetData && (
        <div>
          <h3>Processed Data:</h3>
          <table>
            <thead>
              <tr>
                <th>Caption</th>
                <th>Sentiment</th>
                <th>Named Entities</th>
              </tr>
            </thead>
            <tbody>
              {spreadsheetData.map((row, index) => (
                <tr key={index}>
                  <td>{row.Caption}</td>
                  <td>{row.Sentiment}</td>
                  <td>{row.Named_Entities}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default App;
