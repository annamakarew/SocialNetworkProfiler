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

  const handleSearch = async () => {
    // Check if the username is empty
    if (!username.trim()) {
      alert('Please enter a valid Instagram username.');
      return;
    }

    setLoading(true);
    setError(null);

    /*try {
      // Make an API call to your backend to fetch Instagram data
      const response = await axios.post(
        'http://localhost:5001/api/fetch-data', 
        { username },
        { headers: { 'Content-Type': 'application/json'}}
      );
      
      // Extract the data from the response
      const { sentiment, objects } = response.data;

      // Update state with the results
      setSentimentData(sentiment);
      setObjectRecognitionData(objects);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch data. Please try again.');
    } finally {
      setLoading(false);
    }*/
    try {
      // Send a POST request to the backend with the username
      const response = await axios.post('http://localhost:5001/api/fetch-data', {
          username,
      });
  
      // Set the response data from the server to state
      setResponseData(response.data);
    } catch (error) {
      console.error('Error posting data:', error);
      setError('Error connecting to the backend.');  // Show error message if something goes wrong
    } finally {
      setLoading(false);  // Set loading to false once the request is completed
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
      {/* Display response data or error */}
      {responseData && (
        <div>
          <h3>Response from Backend:</h3>
          <p>Username: {responseData.username}</p>
        </div>
      )}
      {sentimentData && <SentimentAnalysis data={sentimentData} />}
      {objectRecognitionData && <ObjectRecognition data={objectRecognitionData} />}
    </div>
  );
};

export default App;
