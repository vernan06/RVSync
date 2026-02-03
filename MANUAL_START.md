# RVSync - Manual Startup Guide

All dependencies have been installed. You can start the platform manually using the commands below.

## 1. Start Backend Server
Open a terminal in the `rvsync` folder and run:

```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 2. Start Frontend Server
Open a **new** terminal in the `rvsync` folder and run:

```powershell
cd frontend
python -m http.server 3000
```

## 3. Access
- **App**: http://localhost:3000
- **API**: http://localhost:8080/docs
