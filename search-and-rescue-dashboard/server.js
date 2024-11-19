// Import the required packages
const express = require('express');
const cors = require('cors');

// Create an Express app
const app = express();

// Enable CORS for the frontend origin (http://localhost:3000)
app.use(cors({
  origin: 'http://localhost:3000',  // Allow React to access the server
  methods: ['GET', 'POST', 'OPTIONS'],        // Allow specific HTTP methods
  allowedHeaders: ['Content-Type'], // Allow specific headers (Content-Type)
}));

app.use(express.json())

// Define a simple endpoint to test the connection
app.post('/api/fetch-data', (req, res) => {
  const { username } = req.body;
  // Check if the required data (username) is present
  if (!username) {
    return res.status(400).json({ error: 'Username is required' });
  } 
  res.json({ username });
});

// Start the server on port 5000
app.listen(5001, () => {
  console.log('Backend running on http://localhost:5001');
});
