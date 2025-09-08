"""
Pydantic schemas for data validation in ColdOutreachPythonNoDB.
These models validate external API data and ensure type safety throughout the application.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid
import re


class ApifyProspect(BaseModel):
    """
    Pydantic model to validate raw prospect data from the Apify Apollo scraper actor.
    Validates required fields and handles optional data gracefully.
    """
    
    # Required fields according to canon.yaml schemas.apify_prospect
    first_name: str = Field(..., min_length=1, description="Prospect's first name")
    last_name: str = Field(..., min_length=1, description="Prospect's last name")
    email: str = Field(..., description="Prospect's email address")
    company_name: str = Field(..., min_length=1, description="Company name")
    
    # Optional fields according to canon.yaml schemas.apify_prospect
    title: Optional[str] = Field(None, description="Job title/position")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    company_domain: Optional[str] = Field(None, description="Company website domain")
    company_industry: Optional[str] = Field(None, description="Company industry")
    company_size: Optional[str] = Field(None, description="Company size range")
    location: Optional[str] = Field(None, description="Geographic location")
    
    # Internal processing fields
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Original raw data from Apify")
    
    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        """Ensure LinkedIn URL is properly formatted if provided."""
        if v and not v.startswith(('http://', 'https://')):
            return f"https://{v}"
        return v
    
    @validator('company_domain')
    def validate_company_domain(cls, v):
        """Clean up company domain format."""
        if v:
            # Remove protocol and www if present
            v = v.replace('http://', '').replace('https://', '').replace('www.', '')
            # Remove trailing slash
            v = v.rstrip('/')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format using regex."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    def to_prospect_row(self) -> Dict[str, Any]:
        """
        Convert ApifyProspect to normalized Prospects worksheet row format.
        Returns dict matching the prospects worksheet schema from canon.yaml.
        """
        prospect_id = str(uuid.uuid4())
        company_id = str(uuid.uuid4())  # Will be replaced with actual company lookup
        
        return {
            "id": prospect_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "company_id": company_id,
            "title": self.title or "",
            "linkedin_url": self.linkedin_url or "",
            "phase": "discovered",  # Initial phase per canon requirements
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def to_company_row(self) -> Dict[str, Any]:
        """
        Convert ApifyProspect to normalized Companies worksheet row format.
        Returns dict matching the companies worksheet schema from canon.yaml.
        """
        company_id = str(uuid.uuid4())
        
        return {
            "id": company_id,
            "name": self.company_name,
            "domain": self.company_domain or "",
            "industry": self.company_industry or "",
            "size": self.company_size or "",
            "location": self.location or "",
            "description": "",  # Will be populated during research phase
            "created_at": datetime.now().isoformat()
        }
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True  # Automatically strip whitespace
        validate_assignment = True   # Validate on assignment
        extra = "forbid"            # Reject unexpected fields


class ProspectNormalized(BaseModel):
    """
    Normalized prospect data ready for Google Sheets insertion.
    Matches the prospects worksheet schema exactly.
    """
    id: str
    first_name: str
    last_name: str
    email: str
    company_id: str
    title: str
    linkedin_url: str
    phase: str = "discovered"
    created_at: str
    updated_at: str


class CompanyNormalized(BaseModel):
    """
    Normalized company data ready for Google Sheets insertion.
    Matches the companies worksheet schema exactly.
    """
    id: str
    name: str
    domain: str
    industry: str
    size: str
    location: str
    description: str
    created_at: str
