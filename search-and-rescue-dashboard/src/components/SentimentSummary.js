import React, { useEffect, useState } from 'react';
import axios from 'axios';

const SentimentSummary = () => {
  const [sentimentData, setSentimentData] = useState({ positive: 0, neutral: 0, negative: 0 });

  useEffect(() => {
    axios.get('/api/sentiment-summary')
      .then(response => setSentimentData(response.data))
      .catch(error => console.error('Error fetching sentiment summary:', error));
  }, []);

  return (
    <div className="sentiment-summary">
      <h2>Sentiment Analysis Summary</h2>
      <p>Positive: {sentimentData.positive}%</p>
      <p>Neutral: {sentimentData.neutral}%</p>
      <p>Negative: {sentimentData.negative}%</p>
    </div>
  );
};

export default SentimentSummary;
