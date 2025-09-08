#!/usr/bin/env python3
"""
Diagnostic script to test Google Sheets connection
"""
import os
from dotenv import load_dotenv
from src.clients.sheets_client import SheetsClient
from rich.console import Console

console = Console()

def main():
    console.print("[bold blue]🔍 Google Sheets Connection Diagnostic[/bold blue]")
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    service_account_email = os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL")
    private_key = os.getenv("GOOGLE_PRIVATE_KEY")
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "")
    
    console.print("\n[cyan]📋 Environment Variables Status:[/cyan]")
    console.print(f"  GOOGLE_SHEETS_ID: {'✅ Found' if sheets_id else '❌ Missing'}")
    console.print(f"  GOOGLE_SERVICE_ACCOUNT_EMAIL: {'✅ Found' if service_account_email else '❌ Missing'}")
    console.print(f"  GOOGLE_PRIVATE_KEY: {'✅ Found' if private_key else '❌ Missing'}")
    
    if not all([sheets_id, service_account_email, private_key]):
        console.print("\n[red]❌ Missing environment variables. Please check your .env file.[/red]")
        return
    
    # Inspect private key shape without leaking secrets
    if private_key:
        pk = private_key
        preview = (pk[:30] + "..." + pk[-30:]) if len(pk) > 70 else pk
        has_escaped = "\\n" in pk
        has_real_newlines = '\n' in pk
        has_header = "-----BEGIN" in pk
        has_footer = "END PRIVATE KEY-----" in pk
        console.print("\n[cyan]🔎 Private Key Diagnostics:[/cyan]")
        console.print(f"  length: {len(pk)} chars")
        console.print(f"  starts_with_BEGIN: {'✅' if has_header else '❌'}  ends_with_END: {'✅' if has_footer else '❌'}")
        console.print(f"  contains_escaped_\\n: {'✅' if has_escaped else '❌'}  contains_real_newlines: {'✅' if has_real_newlines else '❌'}")
    else:
        console.print("\n[yellow]⚠️ No GOOGLE_PRIVATE_KEY found; will rely on GOOGLE_SHEETS_CREDENTIALS_PATH if provided[/yellow]")

    console.print("\n[cyan]🔑 Testing Google Sheets Authentication...[/cyan]")
    
    try:
        # Initialize SheetsClient
        sheets_client = SheetsClient(
            sheets_id=sheets_id,
            service_account_email=service_account_email,
            private_key=private_key or "",
            credentials_path=credentials_path
        )
        
        # Test basic operations
        console.print("[green]✅ Authentication successful![/green]")
        
        # Get spreadsheet info
        info = sheets_client.get_worksheet_info()
        console.print(f"\n[bold green]📊 Spreadsheet Connected:[/bold green]")
        console.print(f"  Title: {info['title']}")
        console.print(f"  Worksheets: {info['worksheet_count']}")
        
        # Test reading from Batches worksheet
        try:
            cell_value = sheets_client.read_cell("Batches", "A1")
            console.print(f"  Batches A1: '{cell_value}'")
        except Exception as e:
            console.print(f"  [yellow]Note: Batches worksheet may not exist yet (normal)[/yellow]")
        
        console.print("\n[bold green]🎉 All tests passed! Google Sheets integration is working.[/bold green]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Connection failed: {str(e)}[/red]")
        if credentials_path:
            console.print(f"[yellow]Attempted credentials file: {credentials_path}[/yellow]")
        else:
            console.print("[yellow]Attempted inline private key from .env[/yellow]")
        console.print("\n[yellow]💡 Troubleshooting tips:[/yellow]")
        console.print("1. Ensure the service account has access to the Google Sheet")
        console.print(f"2. Share the sheet with: {service_account_email}")
        console.print("3. If using .env GOOGLE_PRIVATE_KEY, ensure it is multi-line with real newlines and no extra quotes")
        console.print("4. Prefer setting GOOGLE_SHEETS_CREDENTIALS_PATH to the downloaded JSON key file for reliability")

if __name__ == "__main__":
    main()
