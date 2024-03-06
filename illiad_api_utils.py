try:
    import requests
except ImportError:
    print('The requests library is required for this script. Please install it with "pip install requests".')
    exit()
import sys

def check_user(email, api_base, api_key):

    # Check that the email address is associated with a valid user account in ILLiad.
    api_url = api_base + '/Users/ExternalUserID/' + email
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        if response.json()['Cleared'] == 'Yes':
            print('\nUser ' + email + ' confirmed.\n')
        else: 
            print('\nUser ' + email + ' is not cleared to place requests.\n')
            sys.exit()
    
    else:
        print(str(response.status_code) + ': ' + response.json()['Message'] + '\n')
        sys.exit()

def submit_transaction(transaction, api_base, api_key, i):
    
    # Submit transaction data to the ILLiad API.
    api_url = api_base + '/Transaction/'
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    response = requests.post(api_url, headers=headers, json=transaction)
    if response.status_code == 200:
        return response.json()['TransactionNumber'], None

    else:
        error = (f'Error on line {i}: ' + str(response.status_code) + ': ' + response.json()['Message'] + '\n')
        return None, error