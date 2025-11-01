# 🎯 Habit Tracker

A full-stack habit tracking application built with React, FastAPI, and SQLite. Track your daily habits, monitor progress with analytics, and export your data.

## ✨ Features

- **User Authentication**: Secure login and registration
- **Habit Management**: Create, track, and manage habits
- **Progress Analytics**: Visual charts and insights
- **Data Export**: CSV and PDF reports
- **Real-time Updates**: Live progress tracking

## 🚀 Setup

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Git

### Backend Setup

1. **Navigate to backend directory**

   ```bash
   cd backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   python main.py
   ```
   Server runs on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   App runs on `http://localhost:5173`

## 📚 API Documentation

### Authentication Endpoints

#### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Login User

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**

```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

### Habit Endpoints

#### Create Habit

```http
POST /api/habits
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Morning Exercise",
  "htype": "boolean",
  "goal": null,
  "start_date": "2024-01-01"
}
```

#### Get All Habits

```http
GET /api/habits
Authorization: Bearer <token>
```

#### Delete Habit

```http
DELETE /api/habits/{habit_id}
Authorization: Bearer <token>
```

### Habit Logging Endpoints

#### Log Habit Completion

```http
POST /api/habits/{habit_id}/logs
Authorization: Bearer <token>
Content-Type: application/json

{
  "date": "2024-01-15",
  "value": 30,
  "completed": true
}
```

#### Get Habit Logs

```http
GET /api/habits/{habit_id}/logs?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

### Analytics Endpoints

#### Get Habit Insights

```http
GET /api/habits/{habit_id}/insights
Authorization: Bearer <token>
```

#### Get Weekly Trends

```http
GET /api/habits/{habit_id}/trends/weekly
Authorization: Bearer <token>
```

#### Get Monthly Trends

```http
GET /api/habits/{habit_id}/trends/monthly
Authorization: Bearer <token>
```

#### Get Chart Data

```http
GET /api/habits/{habit_id}/chart-data?days=30
Authorization: Bearer <token>
```

### Export Endpoints

#### Export CSV

```http
GET /api/export/csv
Authorization: Bearer <token>
```

#### Export PDF

```http
GET /api/export/pdf
Authorization: Bearer <token>
```

## 🗄️ Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Habits Table

```sql
CREATE TABLE habits (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR NOT NULL,
    htype VARCHAR NOT NULL,  -- 'boolean', 'quantity', 'time'
    goal INTEGER,
    archived BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    start_date DATE NOT NULL
);
```

### Habit Logs Table

```sql
CREATE TABLE habit_logs (
    id INTEGER PRIMARY KEY,
    habit_id INTEGER REFERENCES habits(id),
    date DATE NOT NULL,
    value INTEGER,
    completed BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(habit_id, date)
);
```

**Happy Habit Tracking! 🎯**
