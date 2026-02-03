# RVSync Project Status

**Last Updated:** January 23, 2026

## 🏗️ Architecture
We are using a **SQLite Database** (`rvsync.db`).

### 👤 User Roles
1.  **Students**:
    - Registered via `register.html`.
    - Data stored in `users` table.
    - View Student Dashboard.

2.  **Administrators**:
    - **Login**: `admin@rvce.edu.in` / `admin123`
    - **Access**: Full view of the college structure (Admin Dashboard).

## 🛠️ Recent Changes
- **Admin Redirect**: Admins are now automatically sent to `admin.html`.
- **Admin Panel**: "🔐 Admin" button added to Dashboard for easy access.
- **Sidebar**: Fixed scrolling issue on smaller screens.
- **Security**: Fixed compatibility issues with hashing libraries.

## ⚠️ Important Notes
- **Database**: Ensure `rvsync.db` exists in the backend folder.
- **Admin Account**: Ensure the admin user exists in the database with `is_admin=1`.
