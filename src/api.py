"""
api.py - ILLiad API helpers.

This module provides small wrappers around requests to check a user and submit a transaction
to the ILLiad API. Functions raise domain exceptions (from exceptions.py) for callers to
handle. Logging here is intended for diagnostic context; user-visible messages are produced
in main().

Notes:
- Checks 401/404 explicitly to raise more specific domain exceptions before calling
  response.raise_for_status() to preserve clarity of error type.
- Network/JSON errors are re-raised with "raise ... from e" so original context is preserved.

Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu
Editor: Aditi Singh, NC State Libraries, asingh39@ncsu.edu
"""

import logging
from typing import List, Tuple, Optional

import requests

from exceptions import (
    APIError,
    APIAuthenticationError,
    UserNotFoundError,
    UserNotClearedError,
    TransactionSubmissionError,
)

logger = logging.getLogger(__name__)

def check_user(email: str, api_base: str, api_key: str, messages: List[str]) -> List[str]:
    """
    Verify that a user exists in ILLiad and is cleared to place requests.

    Args:
        email: User email to check.
        api_base: Base URL of the ILLiad API
        api_key: API key for authentication.
        messages: List to append status messages for the caller.

    Returns:
        The updated messages list.

    Raises:
        APIAuthenticationError: when the API returns 401 (invalid credentials).
        UserNotFoundError: when the API returns 404 for the user.
        UserNotClearedError: when the user exists but is not cleared to request materials.
        APIError: for other API / network / response issues.
    """

    # Define the API URL and headers.
    api_url = f"{api_base}/Users/ExternalUserID/{email}"
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    try:
        # Make the API request.
        response = requests.get(api_url, headers=headers, timeout=10)

        # Check common, status codes first for clearer domain errors
        if response.status_code == 401:
            logger.error("API authentication failed (401) for %s", api_url)
            raise APIAuthenticationError("Invalid API key. Check the API credentials in config.py", status_code=401)
        if response.status_code == 404:
            logger.error("User not found: %s", email)
            raise UserNotFoundError(f"User {email} not found.", status_code=404)
        
        # Convert other 4xx/5xx into HTTPError so we can handle uniformly below
        response.raise_for_status()  

        data = response.json()
        cleared = data.get('Cleared')

        # If the user has a "Cleared" status of "Yes", the user is valid.
        if cleared == 'Yes':
            messages.append(f'User {email} confirmed.')
            return messages
        # If the user has a "Cleared" status of "No", the user is not valid.
        if cleared == 'No':
            logger.error("User %s is not cleared to place requests", email)
            raise UserNotClearedError(f'User {email} is not cleared to place requests.')
        # Unexpected response body
        logger.error("Unexpected user status response for %s: %s", email, data)
        raise APIError(f'Unexpected user status for {email}', status_code=response.status_code)
    
    except requests.exceptions.HTTPError as e:
        # Preserve original response status in APIError and keep context.
        status = getattr(e.response, "status_code", None)
        logger.exception("HTTP error checking user %s: %s", email, e)
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
        # JSON decoding errors
        logger.exception("Invalid JSON in user check response for %s", email)
        raise APIError("Invalid response from ILLiad API.") from e

def submit_transaction(
    transaction: dict, api_base: str, api_key: str, i: int
) -> Tuple[Optional[str], str]:
    """
    Submit a single transaction to the ILLiad API.

    Args:
        transaction: The transaction payload (dictionary) to POST.
        api_base: Base URL for the API.
        api_key: API key for authentication.
        i: Entry index (used to make per-entry error messages clearer).

    Returns:
        Tuple (transaction_number, error_message).
        - On success: (transaction_number, "No errors")
        - On client-side API error (4xx): (None, "Error on line i: <status>: <message>")
          (we return an error string so the caller can write it to the results file)
    Raises:
        APIAuthenticationError: when API returns 401.
        TransactionSubmissionError: for server-side (5xx) errors or network/JSON failures.
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
        
        # Client errors: include server message if available and return as per-entry error
        if 400 <= response.status_code < 500:
            message = None
            try:
                message = response.json().get("Message")
            except Exception:
                message = response.text or "Unknown client error"
            logger.error("Transaction submission client error line %s status=%s message=%s", i, response.status_code, message)
            return None, f'Error on line {i}: {response.status_code}: {message}'

        # Server errors: treat as fatal for this submission and raise for logging
        if 500 <= response.status_code < 600:
            text = response.text or "Server error"
            logger.error("Transaction submission server error line %s status=%s response=%s", i, response.status_code, text)
            raise TransactionSubmissionError(f'Fatal server error submitting transaction on line {i}', status_code=response.status_code, response_message=text)

        data = response.json()
        txn_number = data.get('TransactionNumber')
        if not txn_number:
            logger.error("No TransactionNumber returned on line %s: %s", i, data)
            return None, f'Error on line {i}: no transaction number returned'
        
        # If the request is successful, return the transaction number.
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
