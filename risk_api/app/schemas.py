from pydantic import BaseModel
from typing import Literal

class EmployeeFeatures(BaseModel):
    age: int
    years_at_company: int
    job_role: str
    monthly_income: int
    distance_from_home: int
    number_of_promotions: int
    number_of_dependents: int
    job_level: Literal["Entry", "Mid", "Senior"]
    company_size: Literal["Small", "Medium", "Large"]
    education_level: Literal["High School", "Associate Degree", "Bachelor’s Degree", "Master’s Degree", "PhD"]
    marital_status: Literal["Divorced", "Married", "Single"]
    overtime: Literal["Yes", "No"]
    remote_work: Literal["Yes", "No"]
    leadership_opportunities: Literal["Yes", "No"]
    innovation_opportunities: Literal["Yes", "No"]
    gender: Literal["Male", "Female"]
    company_reputation: Literal["Poor", "Fair", "Good", "Excellent"]
    employee_recognition: Literal["Low", "Medium", "High", "Very High"]
    work_life_balance: Literal["Poor", "Fair", "Good", "Excellent"]
    job_satisfaction: Literal["Low", "Medium", "High", "Very High"]
    performance_rating: Literal["Low", "Below Average", "Average", "High"]
