import requests
import creds
import base64
import json
import os


# SkinPort client id + client secret set. Stored in gitignored file. 
clientId = creds.api_key
clientSecret = creds.api_secret

# Option to send an email via gmail account. (gmail_send must be True).
gmail_send = True

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

    # Encoding unicode star character on knife/glove to avoid errors
    gold_char = "★"
    gold_char = gold_char.encode("utf-8")

    new_valid_items = [] # All items that pass filters appended to valid_items 

    for item in response:
        # Item dictonary keys into variables for ease of use
        item_name = item['market_hash_name']
        item_name = item_name.encode('utf-8')
        item_currency = item['currency']
        item_currency = item_currency.encode('utf-8')
        suggested_price = item['suggested_price']
        item_page = item['item_page']
        item_market_page = item['market_page']
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
        if item_min_price > max_price:
            print('MAX PRICE EXCEEDED, SKIPPED')
            continue
        if item_discount >= min_discount:
            print('NOT HIGH ENOUGH DISCOUNT, SKIPPED')
            continue
    
        print(f"Item {item_name[0:10]}... satisfies search filters, adding to valid_items....")
        valid_item_dict = {
            'name':item_name.decode(),
            'price': item_min_price,
            'discount': item_discount,
            'suggested_price': suggested_price,
            'link': item_market_page
        }
        new_valid_items.append(valid_item_dict)

    old_valid_items = None

    # Assigning previous results to variable for comparison
    json_empty = os.stat('prev_output.json').st_size == 0
    if json_empty == False:
        with open("prev_output.json", "r") as f:
            old_valid_items = json.load(f)

    # Now that old results are in memory, we assign 'new' resulsts to prev_output.json, so that they are the old results for next run...
    with open("prev_output.json", "w") as f:
        json.dump(new_valid_items, f)


    if gmail_send == True:
        ### gmail testing 
        sender = creds.gmail_sender
        reciever = creds.gmail_receiver
        import smtplib, ssl

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = sender  # Enter your address
        receiver_email = reciever  # Enter receiver address
        password = creds.app_password
        message = f"""\
Subject: SkinPortAlert: New Item(s) satisfy filters...
"""
        
        for i in new_valid_items:
            if i in old_valid_items:
                new_valid_items.remove(i)
        message = message + "\n" + "The following New Items Have Been Found:"
        for new_item in new_valid_items:
            message = message + "\n"
            message = message + f"Name: {new_item['name']}"
            message = message + "\n"
            message = message + f"Price: {new_item['price']}"
            message = message + "\n"
            message = message + f"SkinPort Suggested Price: {new_item['suggested_price']}"
            message = message + "\n"
            message = message + f"Discount: {new_item['discount']}"
            message = message + "\n"
            message = message + f"LINK: {new_item['link']}"
            message = message + "\n"
        message = message + "\n"
        message = message + "\n" + "The following Items Are An Exact Match of Previously Found items, But Still Satisfy Filters:"
        message = message + "\n"
        print("new_valid_items processed")
        if old_valid_items:    
            for old_item in old_valid_items:
                message = message + "\n"
                message = message + f"Name: {old_item['name']}"
                message = message + "\n"
                message = message + f"Price: {old_item['price']}"
                message = message + "\n"
                message = message + f"SkinPort Suggested Price: {old_item['suggested_price']}"
                message = message + "\n"
                message = message + f"Discount: {old_item['discount']}"
                message = message + "\n"
                message = message + f"LINK: {old_item['link']}"
                message = message + "\n"
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(from_addr=sender_email, to_addrs=receiver_email, msg=message.encode('utf-8'))

        print("EMAIL MESSAGE SENT.")
    else:
        print("Not Attempting to Send Gmail... Re-Run Script To Populate Old Results...")
            # Filters
# min_discount = 22
# min_price = 0
# max_price = 250
# knife_only = True
# glove_only = False
# exclude_stattrak = False

items = calculate_discounts(min_discount=-27, knife_only=True, min_price=170, max_price=250)
