#!/usr/bin/env python3
# illiad_api_utils.py
# Description: Utilities to interact with the ILLiad system using APIs; for use by bulk_ill.py.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Built-in modules
import sys

# Libs
try:
    import requests
except ImportError:
    print('The requests library is required for this script. Please install it with "python3 -m pip install requests".')
    exit()

# Check that the email address is associated with a valid user account in ILLiad.
def check_user(email, api_base, api_key):

        try: 
            # Define the API URL and headers.
            api_url = api_base + '/Users/ExternalUserID/' + email
            headers = {'ContentType': 'application/json', 'ApiKey': api_key}

            # Make the API request.
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                # If the user has a "Cleared" status of "Yes", the user is valid.
                if response.json()['Cleared'] == 'Yes':
                    print('\nUser ' + email + ' confirmed.\n')
                # If the user has a "Cleared" status of "No", the user is not valid.
                elif response.json()['Cleared'] == 'No': 
                    print('\nUser ' + email + ' is not cleared to place requests.\n')
                    sys.exit()
            # If the user is not found, the user is not valid.
            elif response.status_code == 401:
                print('Invalid API key. Please check the API credentials in config.py.\n')
                sys.exit()
            
            # Print any other errors.
            else:
                print(str(response.status_code) + ': ' + response.json()['Message'] + '\n')
                sys.exit()
        
        # Print any errors related to the API request.
        except Exception as e:
            print(e)
            sys.exit()

# Submit a transaction to the ILLiad.
def submit_transaction(transaction, api_base, api_key, i):
    
    # Define the API URL and headers.
    try:
        api_url = api_base + '/Transaction/'
        headers = {'ContentType': 'application/json', 'ApiKey': api_key}

        # Make the API request.
        response = requests.post(api_url, headers=headers, json=transaction)
        
        # If the request is successful, return the transaction number.
        if response.status_code == 200:
            return response.json()['TransactionNumber'], None

        # If the request is not successful, return an error message.
        else:
            error = (f'Error on line {i}: ' + str(response.status_code) + ': ' + response.json()['Message'] + '\n')
            return None, error
    
    # Print any errors related to the API request.
    except Exception as e:
        error = (f'Error on line {i}: ' + str(e) + '\n')
        return None, error