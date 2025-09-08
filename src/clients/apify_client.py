"""
Apify API client for ColdOutreachPythonNoDB.
Handles authentication, actor execution, and dataset retrieval from Apify platform.
"""

import os
import time
from typing import Dict, List, Any, Optional
from apify_client import ApifyClient as ApifyClientSDK
from rich.console import Console
from rich.panel import Panel
from urllib.parse import urlencode
from dotenv import load_dotenv

console = Console()


class ApifyClient:
    """
    Apify client for lead discovery using Apollo scraper.
    
    This client uses the standard Apify Python SDK with the correct actor ID
    and input format as specified in the Apollo Scraper documentation.
    """
    
    def __init__(self, api_token: str, actor_id: str, max_retries: int = 3):
        """
        Initialize Apify client with authentication and configuration.
        
        Args:
            api_token: Apify API token for authentication
            actor_id: Actor ID for the Apollo scraper
            max_retries: Maximum number of retry attempts for failed requests
        """
        # Clean API token to remove any trailing whitespace/newlines
        self.api_token = api_token.strip()
        self.actor_id = actor_id.strip()
        self.max_retries = max_retries
        self.client = ApifyClientSDK(self.api_token)
        
        console.print(f"[cyan]📡 Apify client initialized with actor ID: {self.actor_id}[/cyan]")
    
    def run_actor_and_fetch_data(self, actor_input: Dict[str, Any], 
                                total_records: int = 10) -> List[Dict[str, Any]]:
        """
        Run Apollo scraper actor and return lead data.
        
        Args:
            actor_input: Input data for the scraper (must include 'url' and 'totalRecords')
            total_records: Total number of records to fetch (max 50000)
            
        Returns:
            List of lead data dictionaries
            
        Raises:
            Exception: If actor execution fails
        """
        console.print(f"[cyan]🚀 Running Apollo scraper actor for {total_records} leads...[/cyan]")
        
        try:
            # Prepare actor input in correct format
            run_input = self._validate_actor_input(actor_input)
            
            console.print(f"[cyan]📤 Actor input: {run_input}[/cyan]")
            
            # Run the actor and wait for completion
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            console.print(f"[green]✅ Actor run completed: {run['id']}[/green]")
            
            # Fetch results from the dataset
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            console.print(f"[green]✅ Successfully fetched {len(results)} leads[/green]")
            return results
            
        except Exception as e:
            console.print(f"[red]❌ Actor execution failed: {str(e)}[/red]")
            raise
    
    def _validate_actor_input(self, actor_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize actor input format.
        
        Args:
            actor_input: Raw input data
            
        Returns:
            Validated input dictionary
            
        Raises:
            ValueError: If required fields are missing
        """
        url = actor_input.get("url") or actor_input.get("searchUrl")
        if not url:
            raise ValueError("Missing required 'url' field in actor input")
            
        total_records = actor_input.get("totalRecords") or actor_input.get("numberOfLeads", 10)
        
        return {
            "url": url,
            "totalRecords": min(total_records, 50000),  # Enforce API limit
            "fileName": actor_input.get("fileName", "Apollo Prospects")
        }
    
    
    
    def build_apollo_search_url(self, targets: Dict[str, Any]) -> str:
        """
        Build Apollo search URL with correct parameter names from Apollo docs.
        
        Args:
            targets: Dictionary containing search criteria
            
        Returns:
            Properly formatted Apollo search URL
        """
        base_url = "https://app.apollo.io/#/people"
        
        # Extract search parameters from targets
        company_size = targets.get('company_size', '1-50')
        industry = targets.get('industry', 'Technology')
        location = targets.get('location', 'United States')
        job_titles = targets.get('job_titles', ['CEO', 'Founder', 'CTO'])
        
        # Build search URL with correct Apollo parameter names from docs
        url_params = []
        
        # Company size range - using organizationNumEmployeesRanges[]
        if company_size:
            url_params.append(f"organizationNumEmployeesRanges[]={company_size}")
        
        # Industry keywords - using qOrganizationKeywordTags[]
        if industry:
            url_params.append(f"qOrganizationKeywordTags[]={industry}")
        
        # Geographic locations - using personLocations[]
        if location:
            url_params.append(f"personLocations[]={location}")
        
        # Job titles - using personTitles[] (one parameter per title)
        if job_titles:
            for title in job_titles:
                url_params.append(f"personTitles[]={title}")
        
        # Construct final URL
        if url_params:
            search_url = f"{base_url}?{'&'.join(url_params)}"
        else:
            search_url = base_url
        
        console.print(f"[cyan]🔗 Built Apollo search URL: {search_url}[/cyan]")
        return search_url
    
    def test_connection(self) -> bool:
        """
        Test the Apify API connection and authentication.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            url = f"{self.client.base_url}/users/me"
            response = self.client.http_client.get(url)
            response.raise_for_status()
            
            user_data = response.json()
            username = user_data['data'].get('username', 'Unknown')
            
            console.print(Panel(
                f"[bold green]Apify API Connection Successful! 🎉[/bold green]\n\n"
                f"👤 Username: {username}\n"
                f"🔗 API Endpoint: {self.client.base_url}\n"
                f"✅ Authentication: Working",
                title="✅ Apify Connection Test",
                border_style="green"
            ))
            
            return True
            
        except requests.exceptions.RequestException as e:
            console.print(Panel(
                f"[bold red]Apify API Connection Failed[/bold red]\n\n"
                f"❌ Error: {str(e)}\n\n"
                f"🔧 Troubleshooting Steps:\n"
                f"1. Verify APIFY_API_TOKEN is set correctly\n"
                f"2. Check API token has necessary permissions\n"
                f"3. Ensure network connectivity to Apify API",
                title="🚫 Connection Test Failed",
                border_style="red"
            ))
            
            return False


def create_apify_client_from_env() -> ApifyClient:
    """
    Factory function to create ApifyClient from environment variables.
    
    Returns:
        Configured ApifyClient instance
        
    Raises:
        Exception: If required environment variables are missing
    """
    # Load environment variables from .env file
    load_dotenv()
    
    api_token = os.getenv('APIFY_KEY')
    if not api_token:
        raise Exception(
            "APIFY_KEY environment variable is required. "
            "Please set it in your .env file."
        )
    
    actor_id = os.getenv('ACTOR_ID')
    if not actor_id:
        raise Exception(
            "ACTOR_ID environment variable is required. "
            "Please set it in your .env file."
        )
    
    return ApifyClient(api_token=api_token, actor_id=actor_id)
