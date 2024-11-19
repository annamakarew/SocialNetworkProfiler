import React from 'react';

const SentimentAnalysis = ({ data }) => {
  return (
    <div className="sentiment-analysis">
      <h2>Sentiment Analysis</h2>
      <p>Overall Sentiment: {data.overallSentiment}</p>
      <p>Positive: {data.positive}%</p>
      <p>Negative: {data.negative}%</p>
      <p>Neutral: {data.neutral}%</p>
    </div>
  );
};

export default SentimentAnalysis;
