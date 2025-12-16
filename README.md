# Dynamic Expressive Chatbot

## Setup & Run

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the environment (if using conda):
   ```bash
   conda activate chatdocenv
   ```

3. Install dependencies (if not already installed):
   ```bash
   python -m pip install -r requirements.txt
   ```

4. Configure Environment Variables:
   - Open `.env` and set your `GEMINI_API_KEY`.

5. Seed the Database:
   ```bash
   python seed.py
   ```

6. Run the Server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the Development Server:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

## Architecture

- **Backend**: FastAPI, ChromaDB, Gemini API, WebSockets
- **Frontend**: React (Vite)
- **Flow**:
  1. User sends message.
  2. Backend gets text response + emotion from Gemini.
  3. Backend searches ChromaDB for matching emotion image.
  4. If found, returns image URL.
  5. If not found, returns "generating" status, triggers background image generation, and updates frontend via WebSocket when done.
