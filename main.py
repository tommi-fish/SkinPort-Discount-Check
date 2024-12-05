import requests
import time
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os

class SkinportAPI:
    BASE_URL = "https://api.skinport.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
    def get_items(self, currency: str = "EUR", app_id: int = 730) -> List[Dict]:
        """
        Get market data for all items.
        
        Args:
            currency: Currency code (EUR, USD, etc.)
            app_id: Game ID (730 for CS:GO)
            
        Returns:
            List of items with their market data
        """
        endpoint = f"{self.BASE_URL}/items"
        params = {
            'currency': currency,
            'app_id': app_id,
            'api_key': self.api_key
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

    def get_discounted_items(self, min_discount_percent: float = 10.0, currency: str = "EUR", app_id: int = 730) -> List[Dict]:
        """
        Get items that are discounted by at least the specified percentage.
        
        Args:
            min_discount_percent: Minimum discount percentage to filter by (e.g., 10.0 for 10%)
            currency: Currency code (EUR, USD, etc.)
            app_id: Game ID (730 for CS:GO)
            
        Returns:
            List of items that meet the discount criteria, sorted by discount percentage
        """
        items = self.get_items(currency=currency, app_id=app_id)
        discounted_items = []
        
        for item in items:
            # Get price values, defaulting to None if not present
            suggested_price = item.get('suggested_price')
            current_price = item.get('min_price')  # Using min_price instead of price
            
            # Skip items with missing or invalid prices
            if not suggested_price or not current_price or suggested_price <= 0 or current_price <= 0:
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

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize API with key from environment variable
    api = SkinportAPI(api_key=os.getenv('SKINPORT_API_KEY'))
    try:
        # Get all items first to inspect the data
        items = api.get_items()
        print(f"Total items received: {len(items)}")
        
        # Print details of first item to understand the structure
        if items:
            first_item = items[0]
            print("\nAvailable keys in item:")
            print(sorted(first_item.keys()))
            print("\nFirst item data:")
            print(json.dumps(first_item, indent=2))
        
        # Get items with discount
        min_discount_percent = 5
        discounted_items = api.get_discounted_items(min_discount_percent)
        
        print(f"\nFound {len(discounted_items)} items with {min_discount_percent}%+ discount:")
        for item in discounted_items[:10]:  # Show top 10 discounted items
            print(f"{item['market_hash_name']}: {item['discount_percent']}% off "
                  f"(${item['min_price']/100:.2f} vs ${item['suggested_price']/100:.2f})")  # Updated to use min_price
            
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
