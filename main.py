import requests
import creds
import base64
#import os
#import pandas

# SkinPort client id + client secret set. Stored in gitignored file. 
clientId = creds.api_key
clientSecret = creds.api_secret

# Creating BASIC Authentication header to communicate with API.
clientData = f"{clientId}:{clientSecret}"
encodedData = str(base64.b64encode(clientData.encode("utf-8")), "utf-8")
authorizationHeaderString = f"Basic {encodedData}"

currency = "GBP"

response = requests.get("https://api.skinport.com/v1/items", params={
    "app_id": 730, # CSGO steam app id
    "currency": currency, # Currency 
    "tradable": 0 # Include untradeable items
}).json()


def percent_change(old, new):
    """ Calculates percentage change, used to find 'discount' price which isn't provided via API. """

    pc = round((new - old) / abs(old) * 100, 2)
    return pc



def calculate_discounts(min_discount=0, min_price=0, max_price=100000, knife_only=False, glove_only=False, exclude_stattrak=False):
    """ Iterating over the json sent back by API. Lots of filters based on the configuration. """

    valid_items = [] # All items that pass filters appended to valid_items 

    for item in response:
        
        # Item dictonary keys into variables for ease of use
        item_name = item['market_hash_name']
        item_currency = item['currency']
        suggested_price = item['suggested_price']
        item_page = item['item_page']
        market_page = item['market_page']
        item_min_price = item['min_price']
        item_max_price = item['max_price']
        item_mean_price = item['mean_price']
        item_median_price = item['median_price']
        item_quantity = item['quantity']
        created = item['created_at']
        updated = item['updated_at']

        item_name = item_name.encode("utf-8")

        print(item_name.encode("utf-8"))
        continue
        # No listings exluded:
        if item_min_price or item_max_price == None:
            print('NO PRICE INFO, ITEM SKIPPED.')
            continue
        else:
            print('PRICE INFO PRESENT. ITEM NOT SKIPPED')
            


        # Exclude stattrak filter
        if exclude_stattrak:
            print('Exclude StatTrack FILTER ACTIVE:')
            if "StatTrak" in item_name:
                print('StatTrack, ITEM SKIPPED')
                continue
            else:
                print('NON-StatTrack ITEM, NOT SKIPPED.')

        # Knives Only Filter
        if knife_only:
            print('KNIFE ONLY FILTER ACTIVE:')
            if "★" not in item_name or "Gloves" in item_name:
                print('NON-KNIFE ITEM, SKIPPED.')
                continue
            else:
                print('KNIFE ITEM, NOT SKIPPED.')

        # Gloves Only Filter
        if glove_only:
            print('GLOVE ONLY FILTER ACTIVE:')
            if "★" not in item and "Gloves" not in item_name:
                continue
            else:
                print('GLOVE ITEM, NOT SKIPPED.')

        # Grabbing min price of item, if lower than min price, continue to next loop (vice versa for highest):
        lowest = item_min_price
        if int(lowest) < int(min_price): continue
        highest = max_price
        if highest > max_price: continue

        # If price decrease percentage is not > min_discount, exclude item. 
        item_discount = percent_change(suggested_price, item_min_price)
        if item_discount < min_discount:
            continue
        
        valid_items += item
    return valid_items

# Filters
# min_discount = 22
# min_price = 0
# max_price = 250
# knife_only = True
# glove_only = False
# exclude_stattrak = False

print(calculate_discounts(min_price=60, min_discount=20, knife_only=True, exclude_stattrak=True))