import React, { useEffect, useState } from 'react';
import axios from 'axios';

const SentimentTrend = () => {
  const [trendData, setTrendData] = useState([]);

  useEffect(() => {
    axios.get('/api/sentiment-trend')
      .then(response => setTrendData(response.data))
      .catch(error => console.error('Error fetching sentiment trend:', error));
  }, []);

  // Helper function to generate the points for the line chart
  const generatePoints = (data, width, height) => {
    if (data.length === 0) return '';
    const maxScore = Math.max(...data.map(entry => entry.score));
    const minScore = Math.min(...data.map(entry => entry.score));
    const pointSpacing = width / (data.length - 1);

    return data.map((entry, index) => {
      const x = index * pointSpacing;
      const y = height - ((entry.score - minScore) / (maxScore - minScore)) * height;
      return `${x},${y}`;
    }).join(' ');
  };

  const width = 600;
  const height = 300;
  const points = generatePoints(trendData, width, height);

  return (
    <div className="sentiment-trend">
      <h2>Sentiment Trend Over Time</h2>
      <svg width={width} height={height} style={{ border: '1px solid #ddd' }}>
        <polyline
          fill="none"
          stroke="blue"
          strokeWidth="2"
          points={points}
        />
        {/* Add circles at each point for better visualization */}
        {trendData.map((entry, index) => {
          const pointSpacing = width / (trendData.length - 1);
          const x = index * pointSpacing;
          const y = height - ((entry.score - Math.min(...trendData.map(d => d.score))) / 
              (Math.max(...trendData.map(d => d.score)) - Math.min(...trendData.map(d => d.score)))) * height;
          return (
            <circle key={index} cx={x} cy={y} r="3" fill="blue" />
          );
        })}
      </svg>
    </div>
  );
};

export default SentimentTrend;
