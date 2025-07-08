import requests
import json

# Test the new API endpoints
base_url = 'http://localhost:8000'

print('Testing new Alpaca API endpoints...')

# Test account endpoint
try:
    response = requests.get(f'{base_url}/api/account', timeout=5)
    if response.status_code == 200:
        account = response.json()
        print('✓ Account API working:')
        print(f'  - Equity: ${account.get("equity", "N/A")}')
        print(f'  - Buying Power: ${account.get("buying_power", "N/A")}')
    else:
        print('✗ Account API failed:', response.status_code)
except requests.RequestException as e:
    print('✗ Account API connection failed - backend may not be running')

# Test portfolio endpoint
try:
    response = requests.get(f'{base_url}/api/portfolio', timeout=5)
    if response.status_code == 200:
        portfolio = response.json()
        print('✓ Portfolio API working:')
        print(f'  - Total Value: ${portfolio.get("summary", {}).get("total_value", "N/A")}')
        print(f'  - Positions: {portfolio.get("summary", {}).get("position_count", 0)}')
    else:
        print('✗ Portfolio API failed:', response.status_code)
except requests.RequestException as e:
    print('✗ Portfolio API connection failed - backend may not be running')
    
print('\nNote: If connection failed, start the backend with: uvicorn backend.api.fastapi_app:app --host 0.0.0.0 --port 8000')
