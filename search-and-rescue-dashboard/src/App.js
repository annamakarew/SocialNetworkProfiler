import React from 'react';
import './App.css';
import SentimentSummary from './components/SentimentSummary';
import SentimentTrend from './components/SentimentTrend';
import ObjectRecognition from './components/ObjectRecognition';

const App = () => {
  return (
    <div className="App">
      <h1>Search and Rescue Dashboard</h1>
      <SentimentSummary />
      <SentimentTrend />
      <ObjectRecognition />
    </div>
  );
};

export default App;
