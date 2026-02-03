# RVSync - Learning Management & Career Development Platform

Autonomous, institutional-grade LMS with real-time collaboration, ML-powered career intelligence, and 7 AI models.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Frontend
Open `frontend/index.html` in browser or serve with:
```bash
cd frontend
python -m http.server 3000
```

### Docker
```bash
docker-compose up -d
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Docs: http://localhost:8080/docs

## Features

- 🏠 **Classroom Hub** - Create/manage classrooms, courses, materials
- 💬 **Real-time Chat** - WebSocket messaging
- 📝 **Assignments & Tests** - Submit, grade, auto-score
- 🤖 **Career AI** - 7 ML models for predictions & matching
- 🐙 **GitHub Integration** - Sync repos, extract skills
- 💼 **Opportunity Matching** - AI-powered job matching

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Frontend | HTML5, CSS3, Vanilla JS, Chart.js |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ML | XGBoost, Sentence-BERT, scikit-learn |
| Deployment | Docker, Nginx |

## API Endpoints

- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login (JWT)
- `GET /api/users/profile/me` - Get profile
- `GET /api/classroom/{id}/hub` - Classroom hub
- `POST /api/sync/github/{user_id}` - Sync GitHub
- `GET /api/predict-career/{user_id}` - Career prediction
- `GET /api/opportunities/match/{user_id}` - Job matches

Full API docs at `/docs` when running.

## Project Structure

```
rvsync/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # API endpoints
│   │   └── schemas/         # Pydantic schemas
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Landing page
│   ├── dashboard.html       # Main dashboard
│   ├── hub.html            # Classroom hub
│   ├── chat.html           # Real-time chat
│   ├── profile.html        # Profile + GitHub
│   ├── opportunities.html  # Career matching
│   ├── css/styles.css      # Design system
│   └── js/api.js           # API client
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## License

MIT - Built for RVCE students.
