import requests
import time
import json
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import os
from datetime import datetime
import glob
import base64

class SkinportAPI:
    BASE_URL = "https://api.skinport.com/v1"
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.data_dir = "saved_responses"
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Create authorization header
        if client_id and client_secret:
            credentials = f"{client_id}:{client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            auth_header = f"Basic {encoded_credentials}"
        else:
            auth_header = None
            
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        if auth_header:
            self.session.headers.update({'Authorization': auth_header})
            
    def get_saved_responses(self) -> List[Tuple[str, str]]:
        """Get list of saved response files with their timestamps."""
        files = glob.glob(os.path.join(self.data_dir, "items_*.json"))
        # Return list of tuples (filename, timestamp string from filename)
        return [(f, f.split("items_")[1].split(".json")[0]) for f in files]
        
    def _save_response(self, data: List[Dict]):
        """Save API response with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f"items_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return filename
        
    def _get_latest_response(self) -> Optional[str]:
        """Get the most recent saved response file."""
        saved = self.get_saved_responses()
        if not saved:
            return None
        # Sort by timestamp (newest first) and return the filename
        return sorted(saved, key=lambda x: x[1], reverse=True)[0][0]
        
    def get_items(self, currency: str = "EUR", app_id: int = 730, use_local: bool = False, local_file: Optional[str] = None) -> List[Dict]:
        """
        Get market data for all items.
        
        Args:
            currency: Currency code (EUR, USD, etc.)
            app_id: Game ID (730 for CS:GO)
            use_local: Whether to use locally saved data
            local_file: Specific local file to use (if None, uses most recent)
            
        Returns:
            List of items with their market data
        """
        if use_local:
            try:
                # Use specified file or get latest
                file_path = local_file if local_file else self._get_latest_response()
                if not file_path or not os.path.exists(file_path):
                    raise FileNotFoundError("No saved responses found")
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading local JSON file: {str(e)}")
                return []

        # Ensure we have authentication credentials for live requests
        if not self.client_id or not self.client_secret:
            raise ValueError("Client ID and Secret are required for live requests")

        endpoint = f"{self.BASE_URL}/items"
        params = {
            'currency': currency,
            'app_id': app_id
        }
        
        try:
            response = self.session.get(
                endpoint,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Save the response
            self._save_response(data)
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error details: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            raise

    def get_discounted_items(self, min_discount_percent: float = 10.0, currency: str = "EUR", 
                           app_id: int = 730, min_price: float = 1.0, 
                           use_local: bool = False, local_file: Optional[str] = None) -> List[Dict]:
        """
        Get items that are discounted by at least the specified percentage.
        
        Args:
            min_discount_percent: Minimum discount percentage to filter by (e.g., 10.0 for 10%)
            currency: Currency code (EUR, USD, etc.)
            app_id: Game ID (730 for CS:GO)
            min_price: Minimum current price to include in results
            use_local: Whether to use locally saved data
            local_file: Specific local file to use (if None, uses most recent)
            
        Returns:
            List of items that meet the discount criteria, sorted by discount percentage
        """
        items = self.get_items(currency=currency, app_id=app_id, use_local=use_local, local_file=local_file)
        discounted_items = []
        
        for item in items:
            # Get price values, defaulting to None if not present
            suggested_price = item.get('suggested_price')
            current_price = item.get('min_price')  # Using min_price instead of price
            
            # Skip items with missing or invalid prices, or below minimum price
            if (not suggested_price or not current_price or 
                suggested_price <= 0 or current_price <= 0 or 
                current_price < min_price):
                continue
                
            discount_percent = ((suggested_price - current_price) / suggested_price) * 100
            
            if discount_percent >= min_discount_percent:
                item['discount_percent'] = round(discount_percent, 2)
                discounted_items.append(item)
        
        # Sort by discount percentage (highest first)
        return sorted(discounted_items, key=lambda x: x['discount_percent'], reverse=True)

    def get_sales_history(self, market_hash_name: str, currency: str = "EUR", app_id: int = 730) -> List[Dict]:
        """
        Get sales history for a specific item.
        
        Args:
            market_hash_name: The item's market hash name
            currency: Currency code (EUR, USD, etc.)
            app_id: Game ID (730 for CS:GO)
            
        Returns:
            List of recent sales
        """
        endpoint = f"{self.BASE_URL}/sales"
        params = {
            "market_hash_name": market_hash_name,
            "currency": currency,
            "app_id": app_id
        }
        
        try:
            response = self.session.get(
                endpoint,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error details: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            raise

def format_currency(amount: float, currency: str) -> str:
    """Format currency amount with appropriate symbol."""
    currency_symbols = {
        "EUR": "€",
        "USD": "$",
        "GBP": "£"
    }
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"

def display_menu():
    """Display the main menu options."""
    print("\n=== Skinport Discount Checker ===")
    print("1. View Discounted Items")
    print("2. View Item Sales History")
    print("3. View All Items")
    print("4. View Saved Responses")
    print("5. Exit")
    return input("\nSelect an option (1-5): ")

def select_data_source(api: SkinportAPI) -> Tuple[bool, Optional[str]]:
    """Let user choose between API and local data."""
    print("\nSelect data source:")
    print("1. Use API (live data)")
    print("2. Use Local (saved data)")
    choice = input("Select option (1-2): ")
    
    if choice == "2":
        saved = api.get_saved_responses()
        if not saved:
            print("No saved responses found. Using API instead.")
            return False, None
            
        print("\nAvailable saved responses:")
        for i, (file, timestamp) in enumerate(saved, 1):
            dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            print(f"{i}. {dt.strftime('%Y-%m-%d %H:%M:%S')} ({os.path.basename(file)})")
            
        while True:
            try:
                idx = int(input(f"\nSelect response (1-{len(saved)}, or 0 for most recent): "))
                if idx == 0:
                    return True, None
                if 1 <= idx <= len(saved):
                    return True, saved[idx-1][0]
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    return False, None

def display_items(items: List[Dict], currency: str):
    """Display items in a formatted table."""
    if not items:
        print("\nNo items found.")
        return

    print("\n{:<40} {:<15} {:<15} {:<10}".format(
        "Item Name", "Current Price", "Suggested Price", "Discount %"))
    print("-" * 80)
    
    for item in items:
        name = item['market_hash_name'][:39]
        current = format_currency(item['min_price'], currency)
        suggested = format_currency(item.get('suggested_price', 0), currency)
        discount = f"{item.get('discount_percent', 0):.1f}%"
        
        print("{:<40} {:<15} {:<15} {:<10}".format(
            name, current, suggested, discount))

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize API with credentials from environment
    client_id = os.getenv('SKINPORT_CLIENT_ID')
    client_secret = os.getenv('SKINPORT_CLIENT_SECRET')
    api = SkinportAPI(client_id, client_secret)
    
    # Default settings
    currency = "EUR"
    app_id = 730  # CS:GO
    
    while True:
        choice = display_menu()
        
        if choice in ["1", "2", "3"]:
            use_local, local_file = select_data_source(api)
        
        if choice == "1":
            min_discount = float(input("\nEnter minimum discount percentage (e.g., 10): "))
            min_price = float(input("Enter minimum price (e.g., 1.00): "))
            print("\nFetching discounted items...")
            items = api.get_discounted_items(min_discount, currency, app_id, min_price, 
                                          use_local=use_local, local_file=local_file)
            display_items(items, currency)
            
        elif choice == "2":
            item_name = input("\nEnter item name: ")
            print("\nFetching sales history...")
            try:
                history = api.get_sales_history(item_name, currency, app_id)
                if history:
                    print("\nRecent sales:")
                    for sale in history[:10]:  # Show last 10 sales
                        price = format_currency(sale.get('price', 0), currency)
                        time_str = time.strftime('%Y-%m-%d %H:%M:%S', 
                                               time.localtime(sale.get('created_at', 0)))
                        print(f"{time_str}: {price}")
                else:
                    print("No sales history found.")
            except Exception as e:
                print(f"Error fetching sales history: {str(e)}")
                
        elif choice == "3":
            print("\nFetching all items...")
            items = api.get_items(currency, app_id, use_local=use_local, local_file=local_file)
            display_items(items, currency)
            
        elif choice == "4":
            saved = api.get_saved_responses()
            if not saved:
                print("\nNo saved responses found.")
            else:
                print("\nSaved responses:")
                for file, timestamp in saved:
                    dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                    print(f"{dt.strftime('%Y-%m-%d %H:%M:%S')} ({os.path.basename(file)})")
            
        elif choice == "5":
            print("\nGoodbye!")
            break
            
        else:
            print("\nInvalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
