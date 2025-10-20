from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Habit schemas
class HabitCreate(BaseModel):
    name: str
    htype: str
    goal: Optional[int] = None
    start_date: date

class HabitOut(BaseModel):
    id: int
    name: str
    htype: str
    goal: Optional[int]
    archived: bool
    created_at: datetime
    start_date: date
    
    class Config:
        from_attributes = True

# Habit log schemas
class HabitLogUpsert(BaseModel):
    date: date
    value: Optional[int] = None
    completed: Optional[bool] = None

class HabitLogOut(BaseModel):
    id: int
    habit_id: int
    date: date
    value: Optional[int]
    completed: bool
    
    class Config:
        from_attributes = True

# Insight schemas
class InsightOut(BaseModel):
    habit_id: int
    name: str
    seven_day_streak: int
    twenty_eight_day_streak: int
    avg_completion_percent: float
