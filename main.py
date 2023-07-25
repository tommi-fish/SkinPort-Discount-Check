import requests
import creds
import base64

# SkinPort client id + client secret set. Stored in gitignored file. 
clientId = creds.api_key
clientSecret = creds.api_secret

# Creating BASIC Authentication header to communicate with API. 
clientData = f"{clientId}:{clientSecret}"
encodedData = str(base64.b64encode(clientData.encode("utf-8")), "utf-8")
authorizationHeaderString = f"Basic {encodedData}"