import requests
from config import api_key, api_base

email = 'kmblakeadasdsd@ncsu.edu'
api_url = api_base + '/Users/ExternalUserID/' + email

headers = {'ContentType': 'application/json', 'ApiKey': api_key}
    
response = requests.get(api_url, headers=headers)

print(response.json())