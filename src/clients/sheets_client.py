"""
Google Sheets Client for ColdOutreachPythonNoDB
Handles all Google Sheets operations with service account authentication.
"""

import os
import json
import gspread
from typing import List, Dict, Any, Optional
from google.oauth2.service_account import Credentials
from rich.console import Console
from rich.panel import Panel

console = Console()

class SheetsClient:
    """
    Google Sheets client with service account authentication.
    Provides methods for worksheet operations following canon configuration.
    """
    
    def __init__(self, sheets_id: str, service_account_email: str, private_key: str, credentials_path: str = ""):
        """
        Initialize Google Sheets client with service account credentials.
        
        Args:
            sheets_id: Google Sheets document ID
            service_account_email: Service account email address
            private_key: Service account private key (PEM format)
        """
        self.sheets_id = sheets_id
        self.gc = None
        self.spreadsheet = None
        
        try:
            # Set up scopes for Sheets and Drive access
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # Prefer JSON credentials file if provided
            if credentials_path:
                credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
            else:
                # Clean and format private key properly
                cleaned_private_key = private_key.strip()
                # Strip surrounding quotes if present
                if (cleaned_private_key.startswith('"') and cleaned_private_key.endswith('"')) or \
                   (cleaned_private_key.startswith("'") and cleaned_private_key.endswith("'")):
                    cleaned_private_key = cleaned_private_key[1:-1]
                # Normalize Windows newlines and escaped sequences
                cleaned_private_key = cleaned_private_key.replace('\r\n', '\n').replace('\r', '\n')
                if '\\n' in cleaned_private_key:
                    cleaned_private_key = cleaned_private_key.replace('\\n', '\n')

                # Create service account credentials from provided pieces
                service_account_info = {
                    "type": "service_account",
                    "private_key": cleaned_private_key,
                    "client_email": service_account_email,
                    "token_uri": "https://oauth2.googleapis.com/token"
                }

                credentials = Credentials.from_service_account_info(
                    service_account_info, scopes=scopes
                )
            
            # Initialize gspread client
            self.gc = gspread.authorize(credentials)
            
            # Open the spreadsheet
            self.spreadsheet = self.gc.open_by_key(sheets_id)
            
            console.print(Panel(
                f"[bold green]Google Sheets connection established[/bold green]\n"
                f"📊 Spreadsheet ID: {sheets_id}\n"
                f"✅ Authentication: Service Account\n"
                f"🔑 Service Account: {service_account_email}",
                title="🔗 Sheets Connected",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(Panel(
                f"[bold red]Failed to connect to Google Sheets[/bold red]\n"
                f"❌ Error: {str(e)}\n"
                f"💡 Check your credentials and sheet permissions",
                title="🚫 Connection Error",
                border_style="red"
            ))
            raise
    
    def get_worksheet(self, sheet_name: str):
        """
        Get a worksheet by name.
        
        Args:
            sheet_name: Name of the worksheet
            
        Returns:
            gspread.Worksheet object
        """
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            console.print(Panel(
                f"[bold yellow]Creating new worksheet: {sheet_name}[/bold yellow]\n"
                f"📝 Worksheet will be created automatically",
                title="📋 New Worksheet",
                border_style="yellow"
            ))
            return self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
    
    def get_all_records(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        Get all records from a worksheet as a list of dictionaries.
        
        Args:
            sheet_name: Name of the worksheet
            
        Returns:
            List of dictionaries representing rows
        """
        worksheet = self.get_worksheet(sheet_name)
        return worksheet.get_all_records()
    
    def append_rows(self, sheet_name: str, rows: List[List[Any]], header_row: Optional[List[str]] = None) -> None:
        """
        Append multiple rows to a worksheet, optionally ensuring headers exist.
        
        Args:
            sheet_name: Name of the worksheet
            rows: List of lists representing rows to append
            header_row: Optional header row to ensure exists (will be added if worksheet is empty)
        """
        worksheet = self.get_worksheet(sheet_name)
        
        # Check if we need to add headers
        if header_row:
            try:
                existing_headers = worksheet.row_values(1)
                if not existing_headers or all(cell == "" for cell in existing_headers):
                    # Add header row if worksheet is empty or first row is blank
                    worksheet.insert_row(header_row, 1)
                    console.print(f"[cyan]📋 Added headers to {sheet_name}: {', '.join(header_row)}[/cyan]")
            except Exception as e:
                console.print(f"[yellow]⚠️ Could not check/add headers to {sheet_name}: {str(e)}[/yellow]")
        
        if rows:
            worksheet.append_rows(rows)
            console.print(f"[green]✅ Appended {len(rows)} rows to {sheet_name}[/green]")
    
    def find_and_update_rows(self, sheet_name: str, key_column: str, 
                           key_value: str, update_data: Dict[str, Any]) -> bool:
        """
        Find rows by key and update them (upsert pattern).
        
        Args:
            sheet_name: Name of the worksheet
            key_column: Column name to search for the key
            key_value: Value to search for
            update_data: Dictionary of column:value pairs to update
            
        Returns:
            True if row was found and updated, False if not found
        """
        worksheet = self.get_worksheet(sheet_name)
        
        try:
            # Get all records to find the row
            records = worksheet.get_all_records()
            
            # Find the row index (add 2 for header row and 0-indexing)
            row_index = None
            for idx, record in enumerate(records):
                if str(record.get(key_column, "")) == str(key_value):
                    row_index = idx + 2  # +2 for header and 1-indexing
                    break
            
            if row_index:
                # Update existing row
                header_row = worksheet.row_values(1)
                for col_name, value in update_data.items():
                    if col_name in header_row:
                        col_index = header_row.index(col_name) + 1  # 1-indexing
                        worksheet.update_cell(row_index, col_index, value)
                
                console.print(f"[yellow]🔄 Updated existing row in {sheet_name} where {key_column}={key_value}[/yellow]")
                return True
            else:
                console.print(f"[blue]ℹ️ No existing row found in {sheet_name} where {key_column}={key_value}[/blue]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Error updating row in {sheet_name}: {str(e)}[/red]")
            return False
    
    def upsert_row(self, sheet_name: str, key_column: str, row_data: Dict[str, Any]) -> None:
        """
        Insert or update a row based on a key column (upsert operation).
        
        Args:
            sheet_name: Name of the worksheet
            key_column: Column name to use as the unique key
            row_data: Dictionary of column:value pairs for the row
        """
        key_value = row_data.get(key_column)
        if not key_value:
            console.print(f"[red]❌ No value provided for key column '{key_column}'[/red]")
            return
        
        # Try to update existing row
        updated = self.find_and_update_rows(sheet_name, key_column, key_value, row_data)
        
        if not updated:
            # Insert new row
            worksheet = self.get_worksheet(sheet_name)
            header_row = worksheet.row_values(1)
            
            # Create row in correct column order
            new_row = []
            for header in header_row:
                new_row.append(row_data.get(header, ""))
            
            # If no headers exist, create them from row_data keys
            if not header_row:
                header_row = list(row_data.keys())
                worksheet.append_row(header_row)
                new_row = list(row_data.values())
            
            worksheet.append_row(new_row)
            console.print(f"[green]✅ Inserted new row in {sheet_name} with {key_column}={key_value}[/green]")
    
    def read_cell(self, sheet_name: str, cell: str) -> str:
        """
        Read a specific cell value.
        
        Args:
            sheet_name: Name of the worksheet
            cell: Cell reference (e.g., 'A1')
            
        Returns:
            Cell value as string
        """
        worksheet = self.get_worksheet(sheet_name)
        return worksheet.acell(cell).value or ""
    
    def get_worksheet_info(self) -> Dict[str, Any]:
        """
        Get information about all worksheets in the spreadsheet.
        
        Returns:
            Dictionary with spreadsheet information
        """
        worksheets = self.spreadsheet.worksheets()
        return {
            "spreadsheet_id": self.sheets_id,
            "title": self.spreadsheet.title,
            "worksheet_count": len(worksheets),
            "worksheets": [{"title": ws.title, "rows": ws.row_count, "cols": ws.col_count} for ws in worksheets]
        }
