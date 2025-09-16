import requests
from exceptions import BillyError

def check_user(email: str, api_base: str, api_key: str, messages: list) -> list:
    """
    Checks if the user exists and is cleared in ILLiad via API.
    Appends messages and raises BillyError on failure.
    """

    # Define the API URL and headers.
    api_url = api_base + '/Users/ExternalUserID/' + email
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    try:
        # Make the API request.
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            # If the user has a "Cleared" status of "Yes", the user is valid.
            if response.json()['Cleared'] == 'Yes':
                messages.append('\nUser ' + email + ' confirmed.\n')
                return messages
            # If the user has a "Cleared" status of "No", the user is not valid.
            elif response.json()['Cleared'] == 'No': 
                error_message = '\nUser ' + email + ' is not cleared to place requests.\n'
                raise BillyError(error_message)
        # Raise an error if the API key is not valid.
        elif response.status_code == 401:
            error_message = 'Error: Invalid API key. Please check the API credentials in config.py.\n'
            raise BillyError(error_message)
        # Print any other errors.
        else:
            error_message = ' Error: ' + response.json().get('Message', 'Unknown error') + '\n'
            raise BillyError(error_message)
    except Exception as e:
        raise BillyError(e)

def submit_transaction(transaction: dict, api_base: str, api_key: str, i: int):
    """
    Submits a transaction to ILLiad via API.
    Returns transaction number and error message.
    """
    # Define the API URL and headers.
    try:
        api_url = api_base + '/Transaction/'
        headers = {'ContentType': 'application/json', 'ApiKey': api_key}
        
        # Make the API request.
        response = requests.post(api_url, headers=headers, json=transaction)
        
        # If the request is successful, return the transaction number.
        if response.status_code == 200:
            error = 'No errors'
            return response.json()['TransactionNumber'], error
        
        # If the request is not successful, return an error message.
        else:
            error = (f'Error on line {i}: {response.status_code}: {response.json().get("Message", "Unknown error")}\n')
            return None, error
    # Print any errors related to the API request.
    except Exception as e:
        error = (f'Error on line {i}: {str(e)}\n')
        return None, error