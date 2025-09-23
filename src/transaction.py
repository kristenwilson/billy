from transaction_templates import get_transaction_templates_csv, get_transaction_templates_ris

def create_transaction(filetype, transaction_type, illiad_request_type, illiad_doc_type, email, pickup, entry):
    """
    Returns a dictionary of transaction templates prepopulated with values from the user arguments.
    Also returns the title and author for use in the results file.
    """

    if filetype == 'csv':
        transaction_templates = get_transaction_templates_csv(email, pickup, entry, illiad_request_type, illiad_doc_type)
        title = entry.get('Title', '')
        author = entry.get('Author', '')
    elif filetype == 'ris':
        transaction_templates = get_transaction_templates_ris(email, pickup, entry, illiad_request_type, illiad_doc_type)
        title = entry.get('primary_title', '')
        author = entry.get('authors', '')

    # Check if the transaction type is in the transaction_templates dictionary.
    if transaction_type in transaction_templates:
        # If the Type column contains a valid value, return a transaction using the appropriate template.
        # If the file contains a value for a field, use that value. If not, it will be set to ''.
        transaction = {k: entry.get(v, v) for k, v in transaction_templates[transaction_type].items()}
        return transaction, None, title, author
    # If the Type column contains an invalid value, return an error message and move to the next entry.
    else:
        error_message = f'The Type field contains an unsupported citation type.'
        return None, error_message, title, author

def validate_transaction(transaction):
    """
    Check that the transaction contains all required fields.
    Returns an error message if any required fields are missing, otherwise None.
    """
    required_fields = ['ExternalUserId', 'RequestType', 'ProcessType']
    if transaction['RequestType'] == 'Loan':
        required_fields.append('ItemInfo4')

    missing_fields = [field for field in required_fields if field not in transaction or not transaction[field]]

    # Replaces 'ItemInfo4' with 'Pickup Location' in the error message for user clarity.
    if 'ItemInfo4' in missing_fields:
        missing_fields.remove('ItemInfo4')
        missing_fields.append('Pickup Location')

    # Return an error if the transaction is missing any required fields.
    if missing_fields:
        error_message = f'The following required fields are missing from the transaction: {", ".join(missing_fields)}.'
        return error_message
    return None