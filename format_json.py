import json

# Read the JSON file
with open('items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Write back with proper formatting
with open('items.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
