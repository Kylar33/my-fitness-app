from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
from typing import List, Dict
import models.models as models
from sqlalchemy.orm import Session

class ReportGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def add_header(self, title: str):
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(0, 10, title, ln=True, align="C")
        self.pdf.ln(10)

    def add_section(self, title: str):
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 10, title, ln=True)
        self.pdf.set_font("Arial", "", 12)

    def add_text(self, text: str):
        self.pdf.set_font("Arial", "", 12)
        self.pdf.multi_cell(0, 10, text)

    def add_metric_chart(self, dates: List[datetime], values: List[float], title: str, ylabel: str):
        plt.figure(figsize=(10, 4))
        plt.plot(dates, values)
        plt.title(title)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        plt.close()
        
        self.pdf.image(img_buf, x=10, w=190)
        self.pdf.ln(5)

    def generate_progress_report(self, user_data: Dict, metrics: List[models.UserMetrics], 
                               workout_progress: List[models.WorkoutProgress],
                               nutrition_progress: List[models.NutritionProgress]):
        # Header
        self.add_header(f"Progress Report - {user_data['name']}")
        
        # Basic Information
        self.add_section("User Information")
        self.add_text(f"Name: {user_data['name']}")
        self.add_text(f"Report Period: {user_data['start_date']} to {user_data['end_date']}")
        self.pdf.ln(5)
        
        # Metrics Charts
        if metrics:
            dates = [m.date for m in metrics]
            weights = [m.weight for m in metrics if m.weight]
            body_fats = [m.body_fat for m in metrics if m.body_fat]
            
            if weights:
                self.add_metric_chart(dates, weights, "Weight Progress", "Weight (kg)")
            if body_fats:
                self.add_metric_chart(dates, body_fats, "Body Fat Progress", "Body Fat %")
        
        # Progress Statistics
        self.add_section("Progress Statistics")
        completion_rate = user_data.get('completion_rates', {})
        self.add_text(f"Workout Completion Rate: {completion_rate.get('workout', {}).get('rate', 0)}%")
        self.add_text(f"Nutrition Plan Adherence: {completion_rate.get('nutrition', {}).get('rate', 0)}%")
        
        return self.pdf.output(dest='S').encode('latin1')

def generate_user_report(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    """Generate a complete PDF report for a user"""
    # Get user and related data
    user = db.query(models.User).filter(models.User.id == user_id).first()
    metrics = db.query(models.UserMetrics).filter(
        models.UserMetrics.user_id == user_id,
        models.UserMetrics.date.between(start_date, end_date)
    ).all()
    workout_progress = db.query(models.WorkoutProgress).filter(
        models.WorkoutProgress.user_id == user_id,
        models.WorkoutProgress.date.between(start_date, end_date)
    ).all()
    nutrition_progress = db.query(models.NutritionProgress).filter(
        models.NutritionProgress.user_id == user_id,
        models.NutritionProgress.date.between(start_date, end_date)
    ).all()
    
    # Calculate statistics
    from utils.metrics import get_user_completion_rates
    completion_rates = get_user_completion_rates(db, user_id, start_date, end_date)
    
    user_data = {
        "name": user.full_name,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "completion_rates": completion_rates
    }
    
    # Generate PDF
    generator = ReportGenerator()
    return generator.generate_progress_report(user_data, metrics, workout_progress, nutrition_progress)