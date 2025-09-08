"""
Script to process Apollo JSON dataset and upload to Google Sheets in template format.
Uses the existing Apollo data without going through discovery flow again.
"""

import json
import sys
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from src.models.schemas import ApifyProspect
from src.clients.sheets_client import SheetsClient
from src.config.config import Config

console = Console()

def load_apollo_dataset(file_path: str) -> List[Dict[str, Any]]:
    """Load Apollo dataset from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        console.print(f"[green]✅ Loaded {len(data)} records from {file_path}[/green]")
        return data
    except Exception as e:
        console.print(f"[red]❌ Error loading dataset: {str(e)}[/red]")
        raise

def process_apollo_records(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process Apollo records into template format."""
    template_data = []
    invalid_count = 0
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing Apollo records...", total=len(raw_data))
        
        for i, raw_record in enumerate(raw_data):
            try:
                # Skip records without email (invalid for outreach)
                if not raw_record.get('email'):
                    invalid_count += 1
                    progress.update(task, advance=1)
                    continue
                
                # Add raw data to record for template generation
                raw_record["raw_data"] = raw_record.copy()
                
                # Validate with Pydantic model
                prospect = ApifyProspect(**raw_record)
                
                # Convert to template format
                template_row = prospect.to_template_row()
                template_data.append(template_row)
                
            except Exception as e:
                invalid_count += 1
                console.print(f"[yellow]⚠️ Skipping record {i+1}: {str(e)}[/yellow]")
            
            progress.update(task, advance=1)
    
    console.print(
        f"[green]✅ Processing complete: {len(template_data)} valid records, "
        f"{invalid_count} invalid records[/green]"
    )
    
    return template_data

def upload_to_sheets(template_data: List[Dict[str, Any]], config: Config) -> None:
    """Upload template data to Google Sheets."""
    console.print("[cyan]📊 Uploading data to Google Sheets...[/cyan]")
    
    # Get Google Sheets configuration
    sheets_config = config.get_google_sheets_config()
    
    # Initialize sheets client
    sheets_client = SheetsClient(
        sheets_id=sheets_config['sheets_id'],
        service_account_email=sheets_config['service_account_email'],
        private_key=sheets_config['private_key'],
        credentials_path=sheets_config['credentials_path']
    )
    
    # Template header row
    header_row = [
        "Full Name", "Last Name", "First Name", "Email", "Title", 
        "Personal LinkedIn", "Company Name", "Company Website", 
        "Company LinkedIn", "Personal Summary", "Company Background", 
        "Recent Company News", "Key Offerings", "Customer Sentiment", 
        "Company Summary", "Outreach Message"
    ]
    
    # Convert template data to rows
    data_rows = []
    for template_record in template_data:
        row = [
            template_record.get("Full Name", ""),
            template_record.get("Last Name", ""),
            template_record.get("First Name", ""),
            template_record.get("Email", ""),
            template_record.get("Title", ""),
            template_record.get("Personal LinkedIn", ""),
            template_record.get("Company Name", ""),
            template_record.get("Company Website", ""),
            template_record.get("Company LinkedIn", ""),
            template_record.get("Personal Summary", ""),
            template_record.get("Company Background", ""),
            template_record.get("Recent Company News", ""),
            template_record.get("Key Offerings", ""),
            template_record.get("Customer Sentiment", ""),
            template_record.get("Company Summary", ""),
            template_record.get("Outreach Message", "")
        ]
        data_rows.append(row)
    
    # Upload to sheets
    try:
        sheets_client.append_rows("Prospects_Template", data_rows, header_row)
        console.print(f"[green]✅ Successfully uploaded {len(data_rows)} records to Google Sheets[/green]")
    except Exception as e:
        console.print(f"[red]❌ Error uploading to sheets: {str(e)}[/red]")
        raise

def main():
    """Main processing function."""
    console.print(Panel(
        f"[bold blue]Apollo Dataset Processor[/bold blue]\n\n"
        f"📊 Processing Apollo JSON dataset for Google Sheets\n"
        f"🎯 Template Format: 16 columns including computed fields\n"
        f"📋 Direct upload without discovery flow\n\n"
        f"Pipeline: JSON Load → Data Validation → Template Mapping → Sheets Upload",
        title="🚀 Apollo Data Processing",
        border_style="blue"
    ))
    
    try:
        # Load configuration
        config = Config()
        
        # Load Apollo dataset
        dataset_path = "dataset_apollo-io-scraper_2025-09-08_09-00-23-234.json"
        raw_data = load_apollo_dataset(dataset_path)
        
        # Process records into template format
        template_data = process_apollo_records(raw_data)
        
        if not template_data:
            console.print("[red]❌ No valid records to upload[/red]")
            return
        
        # Upload to Google Sheets
        upload_to_sheets(template_data, config)
        
        # Success panel
        console.print(Panel(
            f"[bold green]Apollo Dataset Processing Complete! 🎉[/bold green]\n\n"
            f"📊 **Processing Results:**\n"
            f"• Total records processed: {len(raw_data)}\n"
            f"• Valid template records: {len(template_data)}\n"
            f"• Success rate: {(len(template_data)/len(raw_data)*100):.1f}%\n\n"
            f"💾 **Google Sheets Updates:**\n"
            f"• Sheet: Prospects_Template\n"
            f"• Records uploaded: {len(template_data)}\n"
            f"• Template format: 16 columns\n\n"
            f"✅ Data ready for outreach campaigns\n"
            f"✅ All template fields populated from Apollo data",
            title="✅ Processing Success",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[bold red]Apollo Dataset Processing Failed[/bold red]\n\n"
            f"❌ Error: {str(e)}\n\n"
            f"🔧 Troubleshooting:\n"
            f"1. Check Apollo JSON file exists\n"
            f"2. Verify Google Sheets permissions\n"
            f"3. Review configuration settings",
            title="🚫 Processing Failed",
            border_style="red"
        ))
        raise

if __name__ == "__main__":
    main()
