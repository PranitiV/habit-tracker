import csv
from io import StringIO, BytesIO
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from models import Habit, HabitLog
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF

def generate_csv_report(db: Session, user_id: int) -> str:
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Habit Tracker Report", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])
    
    habits = db.query(Habit).filter(Habit.user_id == user_id, Habit.archived == False).all()
    
    for habit in habits:
        writer.writerow([f"Habit: {habit.name}"])
        if habit.goal:
            writer.writerow([f"Goal: {habit.goal}"])
        writer.writerow(["Date", "Completed", "Value"])
        
        logs = db.query(HabitLog).filter(HabitLog.habit_id == habit.id).order_by(HabitLog.date.desc()).all()
        for log in logs:
            writer.writerow([log.date, "Yes" if log.completed else "No", log.value or ""])
        
        writer.writerow([])
    
    return output.getvalue()

def create_daily_chart(logs_data):
    drawing = Drawing(400, 200)
    
    dates = []
    completion_data = []
    
    for log in logs_data:
        dates.append(log['date'].strftime('%m/%d'))
        completion_data.append(1 if log['completed'] else 0)
    
    if not completion_data:
        return drawing
    
    if len(dates) > 15:
        dates = dates[-15:]
        completion_data = completion_data[-15:]
    
    chart = HorizontalLineChart()
    chart.x = 50
    chart.y = 50
    chart.height = 120
    chart.width = 300
    chart.data = [completion_data]
    chart.lines[0].strokeColor = colors.HexColor('#10b981')
    chart.lines[0].strokeWidth = 2
    
    chart.categoryAxis.categoryNames = dates
    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.labels.fontSize = 8
    
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 1
    chart.valueAxis.labels.fontSize = 8
    
    drawing.add(chart)
    return drawing

def create_weekly_chart(weekly_data):
    drawing = Drawing(400, 200)
    
    if not weekly_data:
        return drawing
    
    weeks = []
    completion_rates = []
    
    for week in weekly_data:
        weeks.append(week['week'])
        completion_rates.append(week['completion_rate'])
    
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 120
    chart.width = 300
    chart.data = [completion_rates]
    chart.bars[0].fillColor = colors.HexColor('#10b981')
    
    chart.categoryAxis.categoryNames = weeks
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    
    drawing.add(chart)
    return drawing

def create_monthly_chart(monthly_data):
    drawing = Drawing(400, 200)
    
    if not monthly_data:
        return drawing
    
    months = []
    completion_rates = []
    
    for month in monthly_data:
        months.append(month['month'])
        completion_rates.append(month['completion_rate'])
    
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 120
    chart.width = 300
    chart.data = [completion_rates]
    chart.bars[0].fillColor = colors.HexColor('#3b82f6')
    
    chart.categoryAxis.categoryNames = months
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    
    drawing.add(chart)
    return drawing

def get_daily_logs_for_chart(db: Session, habit_id: int, days: int = 30):
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
            "date": current_date,
            "completed": log.completed if log else False,
            "value": log.value if log else None
        })
    
    return chart_data

def get_weekly_trend(db: Session, habit_id: int):
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

def get_monthly_trend(db: Session, habit_id: int):
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

def generate_pdf_report(db: Session, user_id: int) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=12,
    )
    
    story = []
    
    story.append(Paragraph("Habit Tracker Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    habits = db.query(Habit).filter(Habit.user_id == user_id, Habit.archived == False).all()
    
    for idx, habit in enumerate(habits):
        if idx > 0:
            story.append(PageBreak())
        
        story.append(Paragraph(f"Habit: {habit.name}", heading_style))
        if habit.goal:
            story.append(Paragraph(f"Goal: {habit.goal}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        daily_data = get_daily_logs_for_chart(db, habit.id, 15)
        weekly_data = get_weekly_trend(db, habit.id)
        monthly_data = get_monthly_trend(db, habit.id)
        
        story.append(Paragraph("Daily Completion Trend (Last 15 Days)", heading_style))
        daily_chart = create_daily_chart(daily_data)
        story.append(daily_chart)
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Weekly Completion Rate", heading_style))
        weekly_chart = create_weekly_chart(weekly_data)
        story.append(weekly_chart)
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Monthly Completion Rate", heading_style))
        monthly_chart = create_monthly_chart(monthly_data)
        story.append(monthly_chart)
        story.append(Spacer(1, 0.2*inch))
        
        logs = db.query(HabitLog).filter(HabitLog.habit_id == habit.id).order_by(HabitLog.date.desc()).all()
        table_data = [["Date", "Completed", "Value"]]
        for log in logs:
            table_data.append([str(log.date), "Yes" if log.completed else "No", str(log.value or "")])
        
        if len(table_data) > 1:
            story.append(Paragraph("Detailed Logs", heading_style))
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
        
        story.append(Spacer(1, 0.3*inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
