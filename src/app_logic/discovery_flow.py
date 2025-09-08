"""
Discovery Flow for ColdOutreachPythonNoDB.
Implements the complete lead discovery workflow using Apify integration with dependency injection.
"""

import uuid
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID
from pydantic import ValidationError

from ..clients.apify_client import ApifyClient
from ..clients.sheets_client import SheetsClient
from ..models.schemas import ApifyProspect, ProspectNormalized, CompanyNormalized

console = Console()


class DiscoveryFlow:
    """
    Lead discovery workflow controller with dependency injection.
    Handles the complete pipeline from Apify data retrieval to Google Sheets normalization.
    """
    
    def __init__(self, apify_client: ApifyClient, sheets_client: SheetsClient):
        """
        Initialize DiscoveryFlow with injected dependencies.
        
        Args:
            apify_client: Configured ApifyClient for API interactions
            sheets_client: Configured SheetsClient for Google Sheets operations
        """
        self.apify_client = apify_client
        self.sheets_client = sheets_client
        
        console.print("[cyan]🔧 DiscoveryFlow initialized with dependency injection[/cyan]")
    
    def run(self, total_records: int, targets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete lead discovery workflow.
        
        Args:
            total_records: Maximum number of records to discover
            targets: Target criteria for Apollo search
            actor_id: Apify actor ID for Apollo scraping
            
        Returns:
            Dictionary with execution results and statistics
        """
        # Start panel per UX flow guidelines
        console.print(Panel(
            f"[bold blue]Lead Discovery Workflow Started[/bold blue]\n\n"
            f"📊 Target Records: {total_records}\n"
            f"🎯 Search Criteria: {self._format_targets(targets)}\n"
            f"🤖 Apollo Scraper: Synchronous Endpoint\n\n"
            f"Pipeline: Apollo Search → Data Validation → Sheets Normalization",
            title="🚀 Phase 2: Lead Discovery",
            border_style="blue"
        ))
        
        results = {
            "total_requested": total_records,
            "raw_records_fetched": 0,
            "valid_prospects": 0,
            "invalid_prospects": 0,
            "prospects_inserted": 0,
            "companies_inserted": 0,
            "errors": []
        }
        
        try:
            # Step 1: Build Apollo search URL from targets
            console.print("[cyan]🔗 Step 1: Building Apollo search URL...[/cyan]")
            apollo_url = self.apify_client.build_apollo_search_url(targets)
            
            # Step 2: Prepare Apify actor input
            actor_input = self._build_actor_input(apollo_url, total_records, targets)
            
            # Step 3: Run Apify scraper and fetch data
            console.print("[cyan]🚀 Step 2: Running Apollo scraper and fetching data...[/cyan]")
            raw_data = self.apify_client.run_actor_and_fetch_data(
                actor_input=actor_input,
                total_records=total_records
            )
            
            results["raw_records_fetched"] = len(raw_data)
            
            # Step 4: Process records with validation and normalization
            console.print(f"[cyan]🔄 Step 3: Processing {len(raw_data)} records with validation...[/cyan]")
            
            prospects_data, companies_data = self._process_records_with_progress(
                raw_data, results
            )
            
            # Step 5: Upsert data to Google Sheets
            console.print("[cyan]📊 Step 4: Upserting data to Google Sheets...[/cyan]")
            
            if prospects_data:
                prospects_inserted = self._upsert_prospects(prospects_data)
                results["prospects_inserted"] = prospects_inserted
            
            if companies_data:
                companies_inserted = self._upsert_companies(companies_data)
                results["companies_inserted"] = companies_inserted
            
            # Success panel per UX flow guidelines
            self._display_success_results(results)
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            results["errors"].append(error_msg)
            
            # Error panel per UX flow guidelines
            console.print(Panel(
                f"[bold red]Lead Discovery Workflow Failed[/bold red]\n\n"
                f"❌ Error: {error_msg}\n\n"
                f"📊 Partial Results:\n"
                f"• Raw records fetched: {results['raw_records_fetched']}\n"
                f"• Valid prospects: {results['valid_prospects']}\n"
                f"• Prospects inserted: {results['prospects_inserted']}\n\n"
                f"🔧 Troubleshooting:\n"
                f"1. Check Apify API token and actor ID\n"
                f"2. Verify Google Sheets permissions\n"
                f"3. Review target criteria format",
                title="🚫 Discovery Failed",
                border_style="red"
            ))
            
            raise
    
    def _format_targets(self, targets: Dict[str, Any]) -> str:
        """Format targets dictionary for display."""
        formatted = []
        for key, value in targets.items():
            if isinstance(value, list):
                value = ", ".join(value)
            formatted.append(f"{key}: {value}")
        return " | ".join(formatted)
    
    def _build_actor_input(self, apollo_url: str, total_records: int, 
                          targets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build input configuration for the Apollo scraper.
        Based on docs: Only requires Apollo search URL and number of leads.
        
        Args:
            apollo_url: Formatted Apollo search URL
            total_records: Number of records to scrape
            targets: Additional targeting parameters (for reference)
            
        Returns:
            Simplified actor input matching Apollo scraper expectations
        """
        # Simplified input based on Apollo scraper documentation
        actor_input = {
            "searchUrl": apollo_url,
            "numberOfLeads": total_records
        }
        
        console.print(f"[cyan]⚙️ Apollo scraper input: {actor_input}[/cyan]")
        return actor_input
    
    def _process_records_with_progress(self, raw_data: List[Dict[str, Any]], 
                                     results: Dict[str, Any]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process raw records with rich progress bar and validation.
        
        Args:
            raw_data: Raw data from Apify
            results: Results dictionary to update
            
        Returns:
            Tuple of (prospects_data, companies_data)
        """
        prospects_data = []
        companies_data = []
        companies_seen = set()  # Track unique companies
        
        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Processing prospects...", 
                total=len(raw_data)
            )
            
            for i, raw_record in enumerate(raw_data):
                try:
                    # Add raw data to record for debugging
                    raw_record["raw_data"] = raw_record.copy()
                    
                    # Validate with Pydantic model
                    prospect = ApifyProspect(**raw_record)
                    
                    # Convert to normalized formats
                    prospect_row = prospect.to_prospect_row()
                    company_row = prospect.to_company_row()
                    
                    # Use company name as unique identifier for deduplication
                    company_key = company_row["name"].lower().strip()
                    
                    prospects_data.append(prospect_row)
                    results["valid_prospects"] += 1
                    
                    # Add company if not seen before
                    if company_key not in companies_seen:
                        companies_data.append(company_row)
                        companies_seen.add(company_key)
                    
                    # Update prospect with actual company ID
                    prospect_row["company_id"] = company_row["id"]
                    
                except ValidationError as ve:
                    results["invalid_prospects"] += 1
                    
                    # Rich warning for invalid records per canon requirements
                    console.print(
                        f"[yellow]⚠️ Skipping invalid record {i+1}: "
                        f"{self._format_validation_error(ve)}[/yellow]"
                    )
                    
                except Exception as e:
                    results["invalid_prospects"] += 1
                    results["errors"].append(f"Record {i+1}: {str(e)}")
                    
                    console.print(
                        f"[yellow]⚠️ Skipping record {i+1} due to error: {str(e)}[/yellow]"
                    )
                
                progress.update(task, advance=1)
        
        console.print(
            f"[green]✅ Processing complete: {results['valid_prospects']} valid, "
            f"{results['invalid_prospects']} invalid, {len(companies_data)} unique companies[/green]"
        )
        
        return prospects_data, companies_data
    
    def _format_validation_error(self, error: ValidationError) -> str:
        """Format ValidationError for display."""
        errors = []
        for err in error.errors():
            field = " -> ".join(str(x) for x in err["loc"])
            msg = err["msg"]
            errors.append(f"{field}: {msg}")
        return "; ".join(errors)
    
    def _upsert_prospects(self, prospects_data: List[Dict[str, Any]]) -> int:
        """
        Upsert prospects data to Google Sheets.
        
        Args:
            prospects_data: List of normalized prospect records
            
        Returns:
            Number of records inserted
        """
        console.print(f"[cyan]📝 Upserting {len(prospects_data)} prospects to 'Prospects' sheet...[/cyan]")
        
        try:
            # Prepare data for sheets insertion (convert to rows)
            header_row = [
                "id", "first_name", "last_name", "email", "company_id", 
                "title", "linkedin_url", "phase", "created_at", "updated_at"
            ]
            
            data_rows = []
            for prospect in prospects_data:
                row = [
                    prospect["id"],
                    prospect["first_name"],
                    prospect["last_name"],
                    prospect["email"],
                    prospect["company_id"],
                    prospect["title"],
                    prospect["linkedin_url"],
                    prospect["phase"],
                    prospect["created_at"],
                    prospect["updated_at"]
                ]
                data_rows.append(row)
            
            # Use sheets_client to append data
            self.sheets_client.append_rows("Prospects", data_rows, header_row)
            
            console.print(f"[green]✅ Successfully inserted {len(data_rows)} prospects[/green]")
            return len(data_rows)
            
        except Exception as e:
            console.print(f"[red]❌ Failed to upsert prospects: {str(e)}[/red]")
            raise
    
    def _upsert_companies(self, companies_data: List[Dict[str, Any]]) -> int:
        """
        Upsert companies data to Google Sheets.
        
        Args:
            companies_data: List of normalized company records
            
        Returns:
            Number of records inserted
        """
        console.print(f"[cyan]🏢 Upserting {len(companies_data)} companies to 'Companies' sheet...[/cyan]")
        
        try:
            # Prepare data for sheets insertion (convert to rows)
            header_row = [
                "id", "name", "domain", "industry", "size", 
                "location", "description", "created_at"
            ]
            
            data_rows = []
            for company in companies_data:
                row = [
                    company["id"],
                    company["name"],
                    company["domain"],
                    company["industry"],
                    company["size"],
                    company["location"],
                    company["description"],
                    company["created_at"]
                ]
                data_rows.append(row)
            
            # Use sheets_client to append data
            self.sheets_client.append_rows("Companies", data_rows, header_row)
            
            console.print(f"[green]✅ Successfully inserted {len(data_rows)} companies[/green]")
            return len(data_rows)
            
        except Exception as e:
            console.print(f"[red]❌ Failed to upsert companies: {str(e)}[/red]")
            raise
    
    def _display_success_results(self, results: Dict[str, Any]) -> None:
        """Display success panel with detailed results."""
        console.print(Panel(
            f"[bold green]Lead Discovery Workflow Completed Successfully! 🎉[/bold green]\n\n"
            f"📊 **Processing Results:**\n"
            f"• Raw records fetched: {results['raw_records_fetched']}\n"
            f"• Valid prospects: {results['valid_prospects']}\n"
            f"• Invalid prospects: {results['invalid_prospects']}\n"
            f"• Success rate: {(results['valid_prospects']/results['raw_records_fetched']*100):.1f}%\n\n"
            f"💾 **Google Sheets Updates:**\n"
            f"• Prospects inserted: {results['prospects_inserted']}\n"
            f"• Companies inserted: {results['companies_inserted']}\n\n"
            f"✅ Data normalized and ready for Phase 3 (Research)\n"
            f"✅ Progress tracking with rich feedback completed",
            title="✅ Discovery Success",
            border_style="green"
        ))
