from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, timedelta
from typing import List, Dict
from models import Habit, HabitLog, User
from schemas import InsightOut

def create_habit(db: Session, user_id: int, name: str, htype: str, goal: int | None):
    habit = Habit(user_id=user_id, name=name, htype=htype, goal=goal)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

def list_habits(db: Session, user_id: int):
    return db.query(Habit).filter(
        Habit.user_id == user_id,
        Habit.archived == False
    ).all()

def get_habit(db: Session, habit_id: int, user_id: int):
    return db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user_id
    ).first()

def update_habit(db: Session, habit: Habit, name: str | None, goal: int | None, archived: bool | None):
    if name is not None:
        habit.name = name
    if goal is not None:
        habit.goal = goal
    if archived is not None:
        habit.archived = archived
    db.commit()
    db.refresh(habit)
    return habit

def upsert_log(db: Session, habit_id: int, d: date, value: int | None, completed: bool | None):
    q = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date == d
    ).first()
    if q:
        if value is not None:
            q.value = value
        if completed is not None:
            q.completed = completed
        db.commit()
        db.refresh(q)
        return q
    newlog = HabitLog(habit_id=habit_id, date=d, value=value, completed=bool(completed))
    db.add(newlog)
    db.commit()
    db.refresh(newlog)
    return newlog

def logs_in_range(db: Session, habit_id: int, start: date, end: date):
    return db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date >= start,
        HabitLog.date <= end
    ).order_by(HabitLog.date.asc()).all()

def calculate_insights(db: Session, habit_id: int) -> InsightOut:
    """Calculate 7-day and 28-day streaks and average completion percentage"""
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        return None
    
    today = date.today()
    
    seven_day_streak = 0
    for i in range(7):
        check_date = today - timedelta(days=i)
        log = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == check_date
        ).first()
        if log and log.completed:
            seven_day_streak += 1
        else:
            break
    
    twenty_eight_day_streak = 0
    for i in range(28):
        check_date = today - timedelta(days=i)
        log = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == check_date
        ).first()
        if log and log.completed:
            twenty_eight_day_streak += 1
        else:
            break

    start_date = habit.start_date
    total_days = (today - start_date).days + 1
    
    logs_from_start = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date >= start_date,
        HabitLog.date <= today
    ).all()
    
    total_days_completed = sum(1 for log in logs_from_start if log.completed)
    avg_completion_percent = (total_days_completed / total_days * 100) if total_days > 0 else 0.0
    
    return InsightOut(
        habit_id=habit_id,
        name=habit.name,
        seven_day_streak=seven_day_streak,
        twenty_eight_day_streak=twenty_eight_day_streak,
        avg_completion_percent=avg_completion_percent
    )

def get_weekly_trend(db: Session, habit_id: int) -> List[Dict]:
    today = date.today()
    trend_data = []
    
    for week in range(4):
        week_start = today - timedelta(days=(week * 7 + 7))
        week_end = today - timedelta(days=(week * 7))
        
        logs = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date >= week_start,
            HabitLog.date <= week_end
        ).all()
        
        completed = sum(1 for log in logs if log.completed)
        total = len(logs) if logs else 7
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        trend_data.append({
            "week": f"Week {4 - week}",
            "completion_rate": completion_rate,
            "completed_days": completed,
            "total_days": total
        })
    
    return list(reversed(trend_data))

def get_monthly_trend(db: Session, habit_id: int) -> List[Dict]:
    today = date.today()
    trend_data = []
    
    for month in range(3):
        month_start = today - timedelta(days=(month * 30 + 30))
        month_end = today - timedelta(days=(month * 30))
        
        logs = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date >= month_start,
            HabitLog.date <= month_end
        ).all()
        
        completed = sum(1 for log in logs if log.completed)
        total = len(logs) if logs else 30
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        month_name = (today - timedelta(days=(month * 30))).strftime("%B")
        trend_data.append({
            "month": month_name,
            "completion_rate": completion_rate,
            "completed_days": completed,
            "total_days": total
        })
    
    return list(reversed(trend_data))

def get_daily_logs_for_chart(db: Session, habit_id: int, days: int = 30) -> List[Dict]:
    today = date.today()
    start_date = today - timedelta(days=days)
    
    logs = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date >= start_date,
        HabitLog.date <= today
    ).order_by(HabitLog.date.asc()).all()
    
    log_dict = {log.date: log for log in logs}
    
    chart_data = []
    for i in range(days + 1):
        current_date = start_date + timedelta(days=i)
        log = log_dict.get(current_date)
        chart_data.append({
            "date": current_date.isoformat(),
            "completed": log.completed if log else False,
            "value": log.value if log else None
        })
    
    return chart_data
