const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();

app.use(cors({
  origin: 'http://localhost:3000',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type'],
}));

app.use(express.json());

app.post('/api/fetch-data', async (req, res) => {
  const { username } = req.body;

  if (!username) {
    return res.status(400).json({ error: 'Username is required' });
  }

<<<<<<< HEAD
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
=======
  try {
    const response = await axios.post('http://localhost:8000/process', { username });
    res.json(response.data);
  } catch (error) {
    console.error('Error calling Python API:', error);
    res.status(500).json({ error: 'Failed to process data.' });
  }
>>>>>>> 8289d0ab4ee11d8b5439616886b4d5b775c59ca4
});

app.listen(5001, () => {
  console.log('Backend running on http://localhost:5001');
});
