#!/usr/bin/env python3
"""
ColdOutreachPythonNoDB - Main CLI Entry Point
A CLI application for automated cold outreach workflow management.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich import print as rich_print

# Import our clients and configuration
from src.clients.sheets_client import SheetsClient
from src.clients.apify_client import create_apify_client_from_env
from src.app_logic.discovery_flow import DiscoveryFlow
from src.config.config import Config

# Initialize Typer app and Rich console
app = typer.Typer(help="ColdOutreachPythonNoDB - Automated Cold Outreach Pipeline")
console = Console()

@app.command()
def hello(
    name: str = typer.Option("World", "--name", "-n", help="Name to greet")
):
    """
    Test command to verify rich is working with colored output.
    """
    # Start panel
    console.print(Panel(
        f"[bold blue]Hello Command Started[/bold blue]\n"
        f"Greeting: {name}",
        title="🚀 Hello Test",
        border_style="blue"
    ))
    
    # Success panel
    console.print(Panel(
        f"[bold green]Hello, {name}! 👋[/bold green]\n"
        f"Rich formatting is working correctly!\n"
        f"✅ CLI Framework: Typer\n"
        f"✅ UI Library: Rich\n"
        f"✅ Colored output: Enabled",
        title="✅ Success",
        border_style="green"
    ))

@app.command()
def test_sheets():
    """
    Test Google Sheets connection and read from Batches worksheet.
    """
    # Start panel
    console.print(Panel(
        "[bold blue]Testing Google Sheets Connection[/bold blue]\n"
        "Initializing client with service account authentication...",
        title="🧪 Google Sheets Test",
        border_style="blue"
    ))
    
    try:
        # Load configuration
        config = Config()
        sheets_config = config.get_google_sheets_config()
        
        # Initialize SheetsClient with dependency injection
        sheets_client = SheetsClient(
            sheets_id=sheets_config["sheets_id"],
            service_account_email=sheets_config["service_account_email"],
            private_key=sheets_config["private_key"],
            credentials_path=sheets_config.get("credentials_path", "")
        )
        
        # Test reading from Batches worksheet
        console.print("[cyan]📊 Testing read access to 'Batches' worksheet...[/cyan]")
        
        try:
            # Try to read cell A1 from Batches worksheet
            cell_value = sheets_client.read_cell("Batches", "A1")
            
            # Get worksheet info
            sheet_info = sheets_client.get_worksheet_info()
            
            # Success panel
            console.print(Panel(
                f"[bold green]Google Sheets Connection Successful! 🎉[/bold green]\n\n"
                f"📋 Spreadsheet: {sheet_info['title']}\n"
                f"📊 Total Worksheets: {sheet_info['worksheet_count']}\n"
                f"🔍 Batches A1 Value: '{cell_value}'\n\n"
                f"✅ Authentication: Working\n"
                f"✅ Read Access: Confirmed\n"
                f"✅ Worksheet Access: Verified",
                title="✅ Test Passed",
                border_style="green"
            ))
            
            # Display available worksheets
            console.print("\n[bold cyan]Available Worksheets:[/bold cyan]")
            for ws in sheet_info['worksheets']:
                console.print(f"  📄 {ws['title']} ({ws['rows']}x{ws['cols']})")
                
        except Exception as read_error:
            console.print(Panel(
                f"[bold yellow]Partial Success - Authentication OK, Read Issues[/bold yellow]\n"
                f"✅ Connection established successfully\n"
                f"⚠️ Read error: {str(read_error)}\n\n"
                f"💡 This might be normal if 'Batches' worksheet doesn't exist yet.\n"
                f"The client will create worksheets automatically when needed.",
                title="⚠️ Partial Success",
                border_style="yellow"
            ))
        
    except Exception as e:
        console.print(Panel(
            f"[bold red]Google Sheets Connection Failed[/bold red]\n\n"
            f"❌ Error: {str(e)}\n\n"
            f"🔧 Troubleshooting Steps:\n"
            f"1. Verify Google Sheets ID is correct\n"
            f"2. Check service account has access to the sheet\n"
            f"3. Ensure private key format is correct\n"
            f"4. Share the sheet with: gdrive-reader@elevator-cloud.iam.gserviceaccount.com",
            title="🚫 Test Failed",
            border_style="red"
        ))

# Command groups for organized CLI structure
run_app = typer.Typer(help="Run various workflow components")
pull_app = typer.Typer(help="Pull data and analytics")
sync_app = typer.Typer(help="Sync and compliance operations")

app.add_typer(run_app, name="run")
app.add_typer(pull_app, name="pull")
app.add_typer(sync_app, name="sync")

# Placeholder commands for future phases
@run_app.command("discovery")
def run_discovery(
    total: int = typer.Option(10, "--total", "-t", help="Total records to discover")
):
    """Run lead discovery workflow (Phase 2)."""
    try:
        # Load configuration
        config = Config()
        sheets_config = config.get_google_sheets_config()
        
        # Initialize clients with dependency injection
        sheets_client = SheetsClient(
            sheets_id=sheets_config["sheets_id"],
            service_account_email=sheets_config["service_account_email"],
            private_key=sheets_config["private_key"],
            credentials_path=sheets_config.get("credentials_path", "")
        )
        
        apify_client = create_apify_client_from_env()
        
        # Initialize DiscoveryFlow with dependency injection
        discovery_flow = DiscoveryFlow(
            apify_client=apify_client,
            sheets_client=sheets_client
        )
        
        # Define default target criteria
        default_targets = {
            "company_size": "1-1000",
            "industry": "All",
            "location": "Germany",
            "job_titles": ["HR","IT LEITER","Head of IT","CEO","CTO"]
        }
        
        # Run the discovery workflow
        results = discovery_flow.run(
            total_records=total,
            targets=default_targets
        )
        
        # Additional success information
        console.print(f"\n[cyan]💡 Next Steps:[/cyan]")
        console.print(f"• Run [bold]python main.py run research[/bold] to enrich companies with research data")
        console.print(f"• Check your Google Sheets for {results['prospects_inserted']} new prospects")
        
    except Exception as e:
        console.print(Panel(
            f"[bold red]Discovery Command Failed[/bold red]\n\n"
            f"❌ Error: {str(e)}\n\n"
            f"🔧 Troubleshooting Steps:\n"
            f"1. Ensure .env file contains APIFY_KEY and SCRAPER_ENDPOINT\n"
            f"2. Verify Google Sheets configuration\n"
            f"3. Check scraper endpoint is accessible\n"
            f"4. Run 'python main.py test-sheets' to verify connectivity",
            title="🚫 Command Failed",
            border_style="red"
        ))
        raise typer.Exit(1)

@run_app.command("research")
def run_research():
    """Run company research workflow (Phase 3)."""
    console.print(Panel(
        "[bold yellow]Research workflow will be implemented in Phase 3[/bold yellow]",
        title="⏳ Phase 3 Pending",
        border_style="yellow"
    ))

@run_app.command("drafting")
def run_drafting():
    """Run email drafting workflow (Phase 4)."""
    console.print(Panel(
        "[bold yellow]Drafting workflow will be implemented in Phase 4[/bold yellow]",
        title="⏳ Phase 4 Pending",
        border_style="yellow"
    ))

@run_app.command("import")
def run_import(
    sequence_id: str = typer.Option(..., "--sequence-id", help="SalesHandy sequence ID")
):
    """Run SalesHandy import workflow (Phase 5-6)."""
    console.print(Panel(
        f"[bold yellow]Import workflow will be implemented in Phase 5-6[/bold yellow]\n"
        f"Sequence ID: {sequence_id}",
        title="⏳ Phase 5-6 Pending",
        border_style="yellow"
    ))

@run_app.command("full-flow")
def run_full_flow(
    sequence_id: str = typer.Option(..., "--sequence-id", help="SalesHandy sequence ID"),
    total: int = typer.Option(10, "--total", "-t", help="Total records to discover")
):
    """Run the complete outreach pipeline (Phase 8)."""
    console.print(Panel(
        f"[bold yellow]Full pipeline will be implemented in Phase 8[/bold yellow]\n"
        f"Sequence ID: {sequence_id}\n"
        f"Total records: {total}",
        title="⏳ Phase 8 Pending",
        border_style="yellow"
    ))

@pull_app.command("analytics")
def pull_analytics():
    """Pull analytics from SalesHandy (Phase 7)."""
    console.print(Panel(
        "[bold yellow]Analytics pull will be implemented in Phase 7[/bold yellow]",
        title="⏳ Phase 7 Pending",
        border_style="yellow"
    ))

@sync_app.command("dnc")
def sync_dnc():
    """Sync DNC (Do Not Contact) list (Phase 5-6)."""
    console.print(Panel(
        "[bold yellow]DNC sync will be implemented in Phase 5-6[/bold yellow]",
        title="⏳ Phase 5-6 Pending",
        border_style="yellow"
    ))

if __name__ == "__main__":
    app()
