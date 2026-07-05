"""Reusable data contracts for information flowing through CivicAI."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ImageAnalysisResult(BaseModel):
    """Structured description and confidence produced by image analysis."""

    issue_type: str
    description: str
    confidence: float


class SeverityLevel(BaseModel):
    """Constrained severity classification assigned to a civic issue."""

    severity: Literal["Low", "Medium", "High", "Critical"]


class DepartmentInfo(BaseModel):
    """Contact details for the department responsible for an issue."""

    department_name: str
    email: str


class Complaint(BaseModel):
    """Prepared complaint content suitable for submission to a department."""

    title: str
    subject: str
    body: str


class CitizenDetails(BaseModel):
    """Citizen identity and location details supplied with a civic report."""

    full_name: str
    contact_number: str
    location: str


class CivicAgentResult(BaseModel):
    """Structured output produced by the complete CivicAgent workflow."""

    citizen_details: CitizenDetails
    image_analysis: ImageAnalysisResult
    department: DepartmentInfo
    complaint: Complaint
    pdf_path:str


class Report(BaseModel):
    """Complete civic issue report composed from reusable application data."""

    report_id: str
    timestamp: datetime
    image_analysis: ImageAnalysisResult
    severity: SeverityLevel
    department: DepartmentInfo
    complaint: Complaint


class EmailDraft(BaseModel):
    """Email message prepared for review before delivery."""

    recipient: str
    subject: str
    body: str
