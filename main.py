import requests
import logging
import creds
import base64
import json
import os
import datetime

logging.basicConfig(level=logging.INFO, file=f"{datetime.datetime.now()}.log")

def percent_decrease(old, new):
        """ Calculates percentage change, used to find 'discount' price which isn't provided via API. """
        if old is not None and new is not None:
            pc = round((new - old) / abs(old) * 100, 2)
            return pc
        else: return 0 


class SkinPort:

    def __init__(self, min_price:int=0, max_price:int=100000, min_discount:int=0, glove_only:bool=False,
                  knife_only:bool=True, exclude_st:bool=True) -> None:
        self.response = requests.get("https://api.skinport.com/v1/items", params={
                        "app_id": 730, # CSGO steam app id
                        "currency": 'GBP', # Currency 
                        "tradable": 0 # Include untradeable items
                        }).json()
        self.prev_output = None

        self.min_price = min_price
        self.max_price = max_price
        self.min_discount = min_discount
        self.glove_only = glove_only
        self.knife_only = knife_only
        self.exclude_st = exclude_st

    def __str__(self) -> str:
         pass
    
    logging.info("SkinPort __init__ complete...")

    def valid_items(self):
        response = self.response

         

        if len(response) < 0:
            logging.info("Unable to start validation of items... No items present.")
            return
         
        logging.info("Starting validation of items...")
         
        for item in response:

            logging.info(f"Starting item [{item['market_hash_name'][:15]}]")

            # Exclude item if there are no current listings.
            if item['quantity'] == 0:
                 logging.info(f"Skipping Item [{item['market_hash_name'][:15]}] No Active Listings.")

            # Calcutes the discount of current item. 
            item_discount = percent_decrease(item['suggested_price'], item['min_price'])

            # Excludes StatTrak items.
            if self.exclude_st == True:
                 if "StatTrak" in item['market_hash_name']:
                      continue
                 
            # Only include knives filter.
            if self.knife_only == True:
                 if "★" not in item['market_hash_name'] or "Gloves" in item['market_hash_name']:
                      continue
            
            # Only include gloves filter.
            if self.glove_only == True:
                if "★" not in item['market_hash_name'] and "Gloves" not in item['market_hash_name']:
                     continue
            
            # If cheapest listing of item exceeds max price, skip. 
            if item['min_price'] > self.max_price:
                 continue
            
            # If cheapest listing is below the min price, skip.
            if item['min_price'] < self.min_price:
                 continue
            
            # If discount is not high enough, skip.

            # 