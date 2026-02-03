# RVSync - Project Overview

**Version**: 1.0 (Stable)
**Date**: January 23, 2026

---

## 1. Introduction
**RVSync** is a specialized Learning Management & Career Development Platform tailored for RVCE.

## 2. Technical Stack
*   **Backend**: Python (FastAPI)
*   **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (ES6+)
*   **Database**: SQLite (SQLAlchemy ORM)
*   **Server**: Uvicorn (ASGI)
*   **Authentication**: JWT (JSON Web Tokens) + Secure Hashing

---

## 3. Architecture
The application uses a standard 3-tier architecture:
1.  **Client**: HTML/JS Frontend communicating via REST API.
2.  **Server**: Python FastAPI backend handling logic.
3.  **Database**: `rvsync.db` (SQLite) storing Users, Courses, etc.

---

## 4. Key Workflows

### 4.1 Registration
Users register with Name, Email, Password, and USN. Data is stored in the Users table.

### 4.2 Authentication
-   **Student Login**: Standard JWT authentication.
-   **Admin Login**: Users with `is_admin=1` flag in the database are treated as admins.

### 4.3 Admin Access
-   Admins are automatically redirected to `admin.html` upon login.
-   Admins have access to global statistics and management.

---

## 5. Security Features
1.  **Secure Cookies/Tokens**: JWT used for session management.
2.  **Password Hashing**: Industry standard hashing.
3.  **Role Protection**: API endpoints verified against user roles.

