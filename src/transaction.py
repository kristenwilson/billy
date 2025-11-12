"""
transaction.py - Transaction creation and validation.

This module handles the creation and validation of ILLiad transaction payloads.
Functions map citation data (from CSV or RIS) into transaction templates, then validate
that required fields are populated before submission.

Notes:
- create_transaction returns a 4-tuple to support both transaction data and metadata
  (title, author) for results file reporting.
- validate_transaction checks for required fields and returns a human-readable error
  message or None.

Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu
Editor: Aditi Singh, NC State Libraries, asingh39@ncsu.edu
"""

from typing import Dict, Optional, Tuple
from transaction_templates import (
    get_transaction_templates_csv,
    get_transaction_templates_ris,
)


def create_transaction(
    filetype: str,
    transaction_type: str,
    illiad_request_type: str,
    illiad_doc_type: str,
    email: str,
    pickup: str,
    entry: Dict,
) -> Tuple[Optional[Dict], Optional[str], str, str]:
    """
    Create a transaction payload from a citation entry.

    This function maps citation fields from a CSV or RIS entry into an ILLiad
    transaction template. If the citation type is recognized, the transaction is
    populated with values from the entry; unrecognized types return None with an
    error message. Title and author are extracted for inclusion in the results file.

    Args:
        filetype: Either 'csv' or 'ris'.
        transaction_type: Standardized transaction type.
        illiad_request_type: ILLiad request type.
        illiad_doc_type: ILLiad document type.
        email: User email.
        pickup: Pickup location .
        entry: Dict representing a single citation row (from CSV or RIS).

    Returns:
        Tuple (transaction, error_message, title, author).
        - transaction: Dict with ILLiad transaction fields, or None if type is unrecognized.
        - error_message: None if successful, or a string describing the error.
        - title: Citation title (for results reporting).
        - author: Citation author (for results reporting).

    Notes:
        - If filetype is 'csv', title/author are retrieved from standard CSV columns.
        - If filetype is 'ris', title/author are retrieved from RIS-mapped keys
          ('primary_title', 'authors').
        - Authors from RIS may be a list; kept as-is for later formatting.
    """
    # Retrieve the appropriate transaction template set for this file type
    if filetype == 'csv':
        transaction_templates = get_transaction_templates_csv(email, pickup, entry, illiad_request_type, illiad_doc_type)
        title = entry.get('Title', '')
        author = entry.get('Author', '')
    elif filetype == 'ris':
        transaction_templates = get_transaction_templates_ris(email, pickup, entry, illiad_request_type, illiad_doc_type)
        title = entry.get('primary_title', '')
        author = entry.get('authors', '')
    else:
        # Defensive: should not occur if validate_file works correctly.
        return None, "Unknown file type.", "", ""

    # Check if the transaction type is supported (via transaction_templates dictionary).
    if transaction_type in transaction_templates:      
        # If supported, build the transaction by mapping template keys to entry values.
        # For each field in the template, use the entry value if present; otherwise use ''
        transaction = {
            k: entry.get(v, v)
            for k, v in transaction_templates[transaction_type].items()
        }
        return transaction, None, title, author
    
    # Unsupported transaction type: return error and move to the next entry
    else:
        error_message = f'The Type field contains an unsupported citation type.'
        return None, error_message, title, author

def validate_transaction(transaction: Dict) -> Optional[str]:
    """
    Validate that a transaction contains all required fields.

    This function checks for mandatory ILLiad transaction fields. The set of required
    fields depends on the request type Field names are translated to user-friendly names 
    in error messages for clarity.

    Args:
        transaction: Dict representing an ILLiad transaction payload.

    Returns:
        None if validation passes - all required fields present and non-empty.
        A readable error message string if validation fails.

    Notes:
        - 'ItemInfo4' field (pickup location) is renamed to 'Pickup Location' in errors
          for clarity to users.
        - Empty strings and None values are treated as missing.
    """
    # Define the base set of required fields
    required_fields = ['ExternalUserId', 'RequestType', 'ProcessType']
    
    # For Loan requests, require a pickup location (ItemInfo4).
    if transaction['RequestType'] == 'Loan':
        required_fields.append('ItemInfo4')

    # Check which required fields are missing (empty or absent).
    missing_fields = [
        field
        for field in required_fields
        if field not in transaction or not transaction[field]
    ]

    # Replaces 'ItemInfo4' with 'Pickup Location' in the error message for user clarity.
    if 'ItemInfo4' in missing_fields:
        missing_fields.remove('ItemInfo4')
        missing_fields.append('Pickup Location')

    # Return an error if the transaction is missing any required fields.
    if missing_fields:
        error_message = f'The following required fields are missing from the transaction: {", ".join(missing_fields)}.'
        return error_message
    
    # All required fields present and non-empty.
    return None