// Import the required packages
const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');

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

  // Call the Python script with the username
  const pythonProcess = spawn('python3', ['process_instagram.py', username]);
  let output = '';
  let errorOutput = '';

  // Capture Python script stdout
  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python stdout]: ${data}`);
    output += data.toString().trim(); // Ensure trailing newlines are removed
  });

  // Capture Python script stderr
  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python stderr]: ${data}`);
  });

  // Handle the end of the Python process
  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`Python script exited with code ${code}`);
      return res.status(500).json({ error: `Python script exited with code ${code}` });
    }

    try {
      // Parse the Python script output (assumes JSON output for React)
      console.log("Python output:", output);
      const result = JSON.parse(output);
      res.json(result);
    } catch (error) {
      console.error('Error parsing Python script output:', error);
      res.status(500).json({ error: 'Error processing data.' });
    }
  });
});

// Start the server on port 5001
app.listen(5001, () => {
  console.log('Backend running on http://localhost:5001');
});
