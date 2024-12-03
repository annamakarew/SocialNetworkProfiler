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

  try {
    const response = await axios.post('http://localhost:8000/process', { username });
    res.json(response.data);
  } catch (error) {
    console.error('Error calling Python API:', error);
    res.status(500).json({ error: 'Failed to process data.' });
  }
});

app.listen(5001, () => {
  console.log('Backend running on http://localhost:5001');
});
