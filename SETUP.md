# Pantry Pilot - Setup & Installation Guide 🚀

This document outlines the step-by-step setup, run instructions, and compile verification commands for the Pantry Pilot application.

---

## 💾 SQLite Database Persistence
The application includes a serverless, local SQLite database backend (`backend/pantry_pilot.db`).
* **Zero-config**: SQLite runs natively through Python's standard `sqlite3` library. No database server installations or setups are required.
* **Initialization**: The database file is automatically created and populated with schema tables on backend server startup.
* **Offline Resilience**: The client uses optimistic synchronization. If the backend SQLite server is down, the frontend store gracefully falls back to using local browser cache (`localStorage`) automatically.

---

## 🛠️ Option A: Unified Quick Start (Recommended)
You can launch both the Svelte development server and the FastAPI backend concurrently using our root-level launch scripts.

### For macOS & Linux:
1. **Initialize the environments** (Run once):
   ```bash
   python3 -m venv backend/venv
   backend/venv/bin/pip install -r backend/requirements.txt
   npm install
   ```
2. **Configure the Gemini API Key** (Optional; falls back to simulation mode if empty):
   ```bash
   cp backend/.env.example backend/.env
   ```
3. **Launch both servers**:
   ```bash
   ./start.sh
   ```
   *Press `Ctrl+C` in your terminal to shut down both servers safely.*

### For Windows (PowerShell):
1. **Initialize the environments** (Run once):
   ```powershell
   python -m venv backend\venv
   .\backend\venv\Scripts\pip.exe install -r backend\requirements.txt
   npm install
   ```
2. **Configure the Gemini API Key** (Optional; falls back to simulation mode if empty):
   ```powershell
   copy backend\.env.example backend\.env
   ```
3. **Launch both servers**:
   ```powershell
   .\start.ps1
   ```
   *Note: If executed inside a WSL share (path starts with `\\wsl`), the script auto-detects it and runs inside WSL. Press `Ctrl+C` to shut down both servers safely.*

---

## 📦 Option B: Manual Setup (Separate Processes)
If you prefer running the servers in separate terminal tabs:

### 1. Start the ADK Agent Backend (Python)
The backend manages the agentic vision scanner loop. It automatically falls back to simulated offline predictions if running without a Gemini API key.
1. **Setup and activate the virtual environment**:
   ```bash
   python3 -m venv backend/venv
   source backend/venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. **Start the API Server**:
   ```bash
   python backend/main.py
   ```
   The backend API will run locally at `http://localhost:8000`.

### 2. Start the Frontend (Svelte)
The Svelte frontend will automatically auto-probe the backend at startup and switch from **Local Simulator** to **ADK Agent** mode if the API is active.
1. **Install node dependencies**:
   ```bash
   npm install
   ```
2. **Start the Development Server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your web browser.

---

## 🧪 Verification & Bundling Commands

### Run Svelte/TypeScript compiler check:
```bash
npm run check
```

### Compile production build:
```bash
npm run build
```
