# Search-and-Rescue Dashboard Setup Guide

## Installation Instructions

### 1. Backend Setup
#### Navigate to the project root:
```bash
cd search-and-rescue-dashboard
```

#### Install Python dependencies:
```bash
pip install fastapi uvicorn transformers pandas instaloader
```

#### Install Node.js dependencies for the backend:
```bash
npm install
```

### 2. Frontend Setup
#### Navigate to the frontend folder:
```bash
cd frontend
```

#### Install Node.js dependencies for the React frontend:
```bash
npm install
```

---

## Running the Application

### 1. Start the Python API
In the `search-and-rescue-dashboard` folder:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 2. Start the Express Server
In the `search-and-rescue-dashboard` folder (new terminal):
```bash
npm start
```

### 3. Start the React Frontend
In the `frontend` folder (new terminal):
```bash
npm start
```
