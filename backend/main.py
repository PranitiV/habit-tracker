from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date as date_type
import os
from dotenv import load_dotenv

from database import engine, get_db, Base
from models import User, Habit, HabitLog
from schemas import (
    UserCreate, UserLogin, UserOut, HabitCreate, HabitOut, 
    HabitLogUpsert, HabitLogOut, InsightOut
)
from auth import create_access_token, get_current_user, hash_password, verify_password
from crud import upsert_log, logs_in_range, calculate_insights, get_weekly_trend, get_monthly_trend, get_daily_logs_for_chart
from export import generate_csv_report, generate_pdf_report

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Habit Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}
  
# ============ AUTH ENDPOINTS ============

@app.post("/api/auth/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    #Register a new user
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    #Login user and return JWT token
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user": UserOut.from_orm(db_user)}

# ============ HABIT ENDPOINTS ============

@app.post("/api/habits", response_model=HabitOut)
def create_new_habit(
    habit: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Create a new habit
    new_habit = Habit(
        user_id=current_user.id,
        name=habit.name,
        htype=habit.htype,
        goal=habit.goal,
        start_date=habit.start_date
    )
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@app.get("/api/habits", response_model=list[HabitOut])
def get_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Get all active habits for current user
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.archived == False
    ).all()
    return habits

@app.delete("/api/habits/{habit_id}")
def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    habit.archived = True
    db.commit()
    return {"message": "Habit archived"}

# ============ HABIT LOG ENDPOINTS ============

@app.post("/api/habits/{habit_id}/logs", response_model=HabitLogOut)
def log_habit(
    habit_id: int,
    log_data: HabitLogUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Log a habit completion (upsert)
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    log_entry = upsert_log(db, habit_id, log_data.date, log_data.value, log_data.completed)
    return log_entry

@app.get("/api/habits/{habit_id}/logs")
def get_habit_logs(
    habit_id: int,
    start_date: str = None,
    end_date: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Get logs for a habit in a date range
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    start = date_type.fromisoformat(start_date) if start_date else date_type.today() - timedelta(days=30)
    end = date_type.fromisoformat(end_date) if end_date else date_type.today()
    
    logs = logs_in_range(db, habit_id, start, end)
    return [HabitLogOut.from_orm(log) for log in logs]

# ============ INSIGHTS ENDPOINTS ============

@app.get("/api/habits/{habit_id}/insights", response_model=InsightOut)
def get_habit_insights(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Get insights for a specific habit
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return calculate_insights(db, habit_id)

# ============ ANALYTICS ENDPOINTS ============

@app.get("/api/habits/{habit_id}/trends/weekly")
def get_weekly_trends(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Get weekly trend data for a habit
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return get_weekly_trend(db, habit_id)

@app.get("/api/habits/{habit_id}/trends/monthly")
def get_monthly_trends(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Get monthly trend data for a habit
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return get_monthly_trend(db, habit_id)

@app.get("/api/habits/{habit_id}/chart-data")
def get_chart_data(
    habit_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Get daily logs for chart visualization
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return get_daily_logs_for_chart(db, habit_id, days)

# ============ EXPORT ENDPOINTS ============

@app.get("/api/export/csv")
def export_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Export all habits to CSV
    csv_data = generate_csv_report(db, current_user.id)
    filename = f"habit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/pdf")
def export_pdf(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Export all habits to PDF
    pdf_data = generate_pdf_report(db, current_user.id)
    filename = f"habit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return StreamingResponse(
        iter([pdf_data]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
