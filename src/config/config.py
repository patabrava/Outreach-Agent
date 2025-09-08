"""
Configuration management for ColdOutreachPythonNoDB
Loads settings from environment variables and canon.yaml
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration class that loads from environment variables and canon.yaml"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Load canon.yaml configuration
        self.canon_path = Path(__file__).parent.parent.parent / "config_canon.yaml"
        self.canon_config = self._load_canon_config()
        
        # Google Sheets Configuration
        self.google_sheets_id = os.getenv("GOOGLE_SHEETS_ID", "")
        self.google_service_account_email = os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL", "")
        self.google_private_key = os.getenv("GOOGLE_PRIVATE_KEY", "")
        self.google_credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "")
        
        # Fallback to hardcoded values if environment variables not set
        # Provide sensible defaults for non-secret values only
        if not self.google_sheets_id:
            self.google_sheets_id = ""
        if not self.google_service_account_email:
            self.google_service_account_email = ""
    
    def _load_canon_config(self) -> Dict[str, Any]:
        """Load configuration from canon.yaml"""
        try:
            if self.canon_path.exists():
                with open(self.canon_path, 'r') as f:
                    return yaml.safe_load(f) or {}
        except Exception:
            pass
        return {}
    
    def get_google_sheets_config(self) -> Dict[str, str]:
        """Get Google Sheets configuration"""
        return {
            "sheets_id": self.google_sheets_id,
            "service_account_email": self.google_service_account_email,
            "private_key": self.google_private_key,
            "credentials_path": self.google_credentials_path
        }
    
    def get_worksheets_config(self) -> Dict[str, Any]:
        """Get worksheets configuration from canon"""
        return self.canon_config.get("google_sheets", {}).get("worksheets", {})
