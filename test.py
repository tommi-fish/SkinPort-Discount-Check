import requests

response = requests.get(
    'https://api.skinport.com/v1/items',
    params={'currency': 'EUR', 'app_id': 730},
    headers={
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
)

print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"URL: {response.url}")
if response.status_code != 200:
    print(f"Error Text: {response.text}")
