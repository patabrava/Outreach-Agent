"""
Pydantic schemas for data validation in ColdOutreachPythonNoDB.
These models validate external API data and ensure type safety throughout the application.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
import uuid
import re


class ApifyProspect(BaseModel):
    """
    Pydantic model to validate raw prospect data from the Apify Apollo scraper actor.
    Maps Apollo's actual field structure to our normalized schema.
    """
    
    # Required fields - mapped from Apollo structure
    first_name: str = Field(..., min_length=1, description="Prospect's first name")
    last_name: str = Field(..., min_length=1, description="Prospect's last name")
    email: str = Field(..., description="Prospect's email address")
    organization_name: str = Field(..., min_length=1, description="Company name from Apollo")
    
    # Optional fields mapped from Apollo structure
    title: Optional[str] = Field(None, description="Job title/position")
    headline: Optional[str] = Field(None, description="LinkedIn headline")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    organization_website_url: Optional[str] = Field(None, description="Company website URL")
    industry: Optional[str] = Field(None, description="Company industry")
    estimated_num_employees: Optional[str] = Field(None, description="Company size")
    city: Optional[str] = Field(None, description="City location")
    state: Optional[str] = Field(None, description="State location")
    country: Optional[str] = Field(None, description="Country location")
    
    # Additional Apollo fields for template generation
    organization_short_description: Optional[str] = Field(None, description="Company description")
    organization_seo_description: Optional[str] = Field(None, description="Company SEO description")
    keywords: Optional[str] = Field(None, description="Company keywords")
    organization_linkedin_url: Optional[str] = Field(None, description="Company LinkedIn URL")
    organization_founded_year: Optional[int] = Field(None, description="Company founding year")
    organization_annual_revenue_printed: Optional[str] = Field(None, description="Company revenue")
    
    # Internal processing fields
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Original raw data from Apify")
    
    # Computed properties for backward compatibility
    @property
    def company_name(self) -> str:
        """Map organization_name to company_name for compatibility."""
        return self.organization_name
    
    @property
    def company_domain(self) -> Optional[str]:
        """Extract domain from organization_website_url."""
        if self.organization_website_url:
            domain = self.organization_website_url.replace('http://', '').replace('https://', '').replace('www.', '')
            return domain.rstrip('/')
        return None
    
    @property
    def company_industry(self) -> Optional[str]:
        """Map industry to company_industry for compatibility."""
        return self.industry
    
    @property
    def company_size(self) -> Optional[str]:
        """Map estimated_num_employees to company_size for compatibility."""
        return self.estimated_num_employees
    
    @property
    def location(self) -> Optional[str]:
        """Combine city, state, country into location string."""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.country:
            parts.append(self.country)
        return ', '.join(parts) if parts else None
    
    @property
    def effective_title(self) -> Optional[str]:
        """Use title if available, otherwise use headline."""
        return self.title or self.headline
    
    @property
    def full_name(self) -> str:
        """Combine first and last name."""
        return f"{self.first_name} {self.last_name}"
    
    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        """Ensure LinkedIn URL is properly formatted if provided."""
        if v and not v.startswith(('http://', 'https://')):
            return f"https://{v}"
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
            "title": self.effective_title or "",
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
    
    def to_template_row(self) -> Dict[str, Any]:
        """
        Convert ApifyProspect to template format for Google Sheets.
        Maps Apollo data to the exact template structure:
        Full Name, Last Name, First Name, Email, Title, Personal LinkedIn, 
        Company Name, Company Website, Company LinkedIn, Personal Summary,
        Company Background, Recent Company News, Key Offerings, 
        Customer Sentiment, Company Summary, Outreach Message
        """
        # Get additional fields from raw_data if available
        raw = self.raw_data or {}
        
        # Extract computed fields from Apollo data
        full_name = f"{self.first_name} {self.last_name}"
        personal_summary = self._extract_personal_summary()
        company_background = self._extract_company_background()
        key_offerings = self._extract_key_offerings()
        company_summary = self._extract_company_summary()
        
        return {
            "Full Name": full_name,
            "Last Name": self.last_name,
            "First Name": self.first_name,
            "Email": self.email,
            "Title": self.effective_title or "",
            "Personal LinkedIn": self.linkedin_url or "",
            "Company Name": self.company_name,
            "Company Website": self.organization_website_url or "",
            "Company LinkedIn": raw.get('organization_linkedin_url', ''),
            "Personal Summary": personal_summary,
            "Company Background": company_background,
            "Recent Company News": "",  # To be populated during research phase
            "Key Offerings": key_offerings,
            "Customer Sentiment": "",  # To be populated during research phase
            "Company Summary": company_summary,
            "Outreach Message": ""  # To be populated during outreach phase
        }
    
    def _extract_personal_summary(self) -> str:
        """Extract personal summary from headline and title."""
        if hasattr(self, 'headline') and self.headline:
            return self.headline[:200]  # Limit length
        elif self.effective_title:
            return f"{self.effective_title} at {self.company_name}"
        return ""
    
    def _extract_company_background(self) -> str:
        """Extract company background from organization description."""
        raw = self.raw_data or {}
        
        # Try organization_short_description first, then seo_description
        description = raw.get('organization_short_description') or raw.get('organization_seo_description', '')
        
        if description:
            # Clean and truncate description
            clean_desc = description.replace('\n', ' ').replace('\r', ' ')
            return clean_desc[:500]  # Limit to 500 chars for sheets
        return ""
    
    def _extract_key_offerings(self) -> str:
        """Extract key offerings from keywords and industry."""
        raw = self.raw_data or {}
        keywords = raw.get('keywords', '')
        
        if keywords:
            # Extract first few keywords as key offerings
            keyword_list = [k.strip() for k in keywords.split(',')][:5]
            return ', '.join(keyword_list)
        elif self.industry:
            return f"{self.industry} solutions"
        return ""
    
    def _extract_company_summary(self) -> str:
        """Extract company summary from various company fields."""
        raw = self.raw_data or {}
        
        # Build summary from available data
        summary_parts = []
        
        if raw.get('organization_founded_year'):
            summary_parts.append(f"Founded in {raw['organization_founded_year']}")
        
        if self.company_size:
            summary_parts.append(f"{self.company_size} employees")
        
        if raw.get('organization_annual_revenue_printed'):
            summary_parts.append(f"${raw['organization_annual_revenue_printed']} revenue")
        
        if self.location:
            summary_parts.append(f"Located in {self.location}")
        
        if self.industry:
            summary_parts.append(f"{self.industry} industry")
        
        return ' | '.join(summary_parts)
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True  # Automatically strip whitespace
        validate_assignment = True   # Validate on assignment
        extra = "allow"             # Allow extra fields from Apollo to prevent rejection


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
