# Champions Odyssey

A full-stack application with React frontend and FastAPI backend.

## Project Structure

```
Champions-Odyssey/
├── frontend/          # React TypeScript application
│   ├── src/
│   ├── public/
│   └── package.json
└── server/           # FastAPI backend
    ├── main.py
    ├── requirements.txt
    └── README.md
```

## Getting Started

### Frontend (React)

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The React app will be available at `http://localhost:3000`

### Backend (FastAPI)

1. Navigate to the server directory:
```bash
cd server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Development

- Frontend runs on port 3000
- Backend runs on port 8000
- CORS is configured to allow frontend-backend communication
