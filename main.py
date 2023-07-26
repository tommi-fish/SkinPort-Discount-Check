import requests
import creds
import base64
import json
from pathlib import Path
#import pandas

# SkinPort client id + client secret set. Stored in gitignored file. 
clientId = creds.api_key
clientSecret = creds.api_secret

# Creating BASIC Authentication header to communicate with API.
clientData = f"{clientId}:{clientSecret}"
encodedData = str(base64.b64encode(clientData.encode("utf-8")), "utf-8")
authorizationHeaderString = f"Basic {encodedData}"


response = requests.get("https://api.skinport.com/v1/items", params={
    "app_id": 730, # CSGO steam app id
    "currency": 'GBP', # Currency 
    "tradable": 0 # Include untradeable items
}).json()


def percent_change(old, new):
    """ Calculates percentage change, used to find 'discount' price which isn't provided via API. """
    if old is not None and new is not None:
        pc = round((new - old) / abs(old) * 100, 2)
        return pc
    else: return 0


def calculate_discounts(min_discount: int=0, min_price: int=0,
                        max_price:int =100000, knife_only: bool=False,
                        glove_only: bool=False, exclude_stattrak: bool=False):
    """ Iterating over the json sent back by API. Lots of filters based on the configuration. """

    # Creates json if it doesn't exist
    path = Path('./prev_output.json')
    first_run = path.is_file()
    if first_run:
        json_object = json.dumps(response, indent=4)
        with open("prev_output.json", "w") as outfile:
            outfile.write(json_object)

    # Encoding unicode star character on knife/glove to avoid errors
    gold_char = "★"
    gold_char = gold_char.encode("utf-8")

    valid_items = [] # All items that pass filters appended to valid_items 

    for item in response:
        # Item dictonary keys into variables for ease of use
        item_name = item['market_hash_name']
        item_name = item_name.encode('utf-8')
        item_currency = item['currency']
        item_currency = item_currency.encode('utf-8')
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

        item_discount = percent_change(suggested_price, item_min_price)

        print(f"Starting Item: {item_name} Suggested: {suggested_price} Min: {item_min_price} Max: {item_max_price}, Quan:{item_quantity}, Discount:{item_discount}")

        # No listings exluded:
        if item_quantity == 0:
            print(f"No listings for {item_name}, item skipped")
            continue
            

        # Exclude stattrak filter
        if exclude_stattrak:
            print('Exclude StatTrack FILTER ACTIVE:')
            if "StatTrak" in item_name.decode():
                print('ST, ITEM SKIPPED')
                continue
            else:
                print('NON-ST ITEM, NOT SKIPPED.')

        # Knives Only Filter
        if knife_only:
            print('KNIFE ONLY FILTER ACTIVE:')
            if "★" not in item_name.decode() or "Gloves" in item_name.decode():
                print('NON-KNIFE ITEM, SKIPPED.')
                continue
            else:
                print('KNIFE ITEM, NOT SKIPPED.')

        # Gloves Only Filter
        if glove_only:
            print('GLOVE ONLY FILTER ACTIVE:')
            if "★" not in item_name.decode() and "Gloves" not in item_name.decode():
                print('NON-GLOVE ITEM, SKIPPED.')
                continue
            else:
                print('GLOVE ITEM, NOT SKIPPED.')

        # Grabbing min price of item, if lower than min price, continue to next loop (vice versa for highest):
        
        if item_min_price < min_price:
            print('MIN PRICE TOO LOW, SKIPPED.')
            continue
        elif item_min_price > max_price:
            print('MAX PRICE EXCEEDED, SKIPPED')
            continue
        elif item_discount >= min_discount:
            print('NOT HIGH ENOUGH DISCOUNT, SKIPPED')
            continue
    
        print(f"Item {item_name[0:10]}... satisfies search filters, adding to valid_items....")
        valid_items.append(item)

    # Won't re-create json if it is the first run, price comparison logic will only take place if it isn't the first run of script. 
    if first_run == False:
        json_object = json.dumps(response, indent=4)
        with open("prev_output.json", "w") as outfile:
            outfile.write(json_object)

    return valid_items

# Filters
# min_discount = 22
# min_price = 0
# max_price = 250
# knife_only = True
# glove_only = False
# exclude_stattrak = False

items = calculate_discounts(min_discount=10, knife_only=True)
