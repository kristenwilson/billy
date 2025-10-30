import requests
import logging
from exceptions import APIError, APIAuthenticationError, UserNotFoundError, UserNotClearedError, TransactionSubmissionError

logger = logging.getLogger(__name__)

def check_user(email: str, api_base: str, api_key: str, messages: list) -> list:
    """
    Checks if the user exists and is cleared in ILLiad via API.
    Appends messages and raises BillyError on failure.
    """

    # Define the API URL and headers.
    api_url = f"{api_base}/Users/ExternalUserID/{email}"
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    try:
        # Make the API request.
        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 401:
            logger.error("API authentication failed (401) for %s", api_url)
            raise APIAuthenticationError("Invalid API key. Check the API credentials in config.py", status_code=401)
        if response.status_code == 404:
            logger.error("User not found: %s", email)
            raise UserNotFoundError(f"User {email} not found.", status_code=404)
        
        # Raises HTTPError for 4XX/5XX status codes
        response.raise_for_status()  

        data = response.json()
        cleared = data.get('Cleared')
        # If the user has a "Cleared" status of "Yes", the user is valid.
        if cleared == 'Yes':
            messages.append(f'User {email} confirmed.')
            return messages
        # If the user has a "Cleared" status of "No", the user is not valid.
        elif cleared == 'No':
            logger.error("User %s is not cleared to place requests", email)
            raise UserNotClearedError(f'User {email} is not cleared to place requests.')
        else:
            logger.error("Unexpected user status response for %s: %s", email, data)
            raise APIError(f'Unexpected user status for {email}', status_code=response.status_code)
    except requests.exceptions.HTTPError as e:
        logger.exception("HTTP error checking user %s: %s", email, e)
        status = getattr(e.response, "status_code", None)
        raise APIError(f"API error: {e}", status_code=status) from e
    except requests.exceptions.Timeout as e:
        logger.exception("Timeout while checking user %s", email)
        raise APIError("Timeout contacting ILLiad API.") from e
    except requests.exceptions.ConnectionError as e:
        logger.exception("Connection error while checking user %s", email)
        raise APIError("Could not connect to ILLiad API.") from e
    except requests.exceptions.RequestException as e:
        logger.exception("API request failed while checking user %s", email)
        raise APIError("ILLiad API request failed.") from e
    except ValueError as e:
        logger.exception("Invalid JSON in user check response for %s", email)
        raise APIError("Invalid response from ILLiad API.") from e

def submit_transaction(transaction: dict, api_base: str, api_key: str, i: int):
    """
    Submits a transaction to ILLiad via API.
    Returns transaction number and error message.
    """
    # Define the API URL and headers.
    api_url = api_base + '/Transaction/'
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}
    try: 
        # Make the API request.
        response = requests.post(api_url, headers=headers, json=transaction, timeout=15)
        
        if response.status_code == 401:
            logger.error("API authentication failed on submit (401)")
            raise APIAuthenticationError("Invalid API key on submit.", status_code=401)
        
        if 400 <= response.status_code < 500:
            message = None
            try:
                message = response.json().get("Message")
            except Exception:
                message = response.text or "Unknown client error"
            logger.error("Transaction submission client error line %s status=%s message=%s", i, response.status_code, message)
            return None, f'Error on line {i}: {response.status_code}: {message}'

        if 500 <= response.status_code < 600:
            text = response.text or "Server error"
            logger.error("Transaction submission server error line %s status=%s response=%s", i, response.status_code, text)
            raise TransactionSubmissionError(f'Fatal server error submitting transaction on line {i}', status_code=response.status_code, response_message=text)

        data = response.json()
        txn_number = data.get('TransactionNumber')
        if not txn_number:
            logger.error("No TransactionNumber returned on line %s: %s", i, data)
            return None, f'Error on line {i}: no transaction number returned'
        return txn_number, 'No errors'

    # Print any errors related to the API request.
    except requests.exceptions.Timeout as e:
        logger.exception("Timeout while submitting transaction on line %s", i)
        raise TransactionSubmissionError(f'Error on line {i}: request timed out') from e
    except requests.exceptions.ConnectionError as e:
        logger.exception("Connection error while submitting transaction on line %s", i)
        raise TransactionSubmissionError(f'Error on line {i}: connection error') from e
    except requests.exceptions.RequestException as e:
        logger.exception("Request failed while submitting transaction on line %s", i)
        raise TransactionSubmissionError(f'Error on line {i}: request failed: {str(e)}') from e
    except ValueError as e:
        logger.exception("Invalid JSON in submit response on line %s", i)
        raise TransactionSubmissionError(f'Error on line {i}: invalid response') from e
