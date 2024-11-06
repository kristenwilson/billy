#!/usr/bin/env python3
# transaction_utils.py
# Description: Utilities to create and process ILLiad transactions; for use by bulk_ill.py.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Custom modules
from transaction_templates import map_citation_type, get_transaction_templates_csv, get_transaction_templates_ris
from illiad_api_utils import submit_transaction
from validation_utils import validate_transaction
from file_utils import *
from rispy_utils import map_rispy

# Configuration
from config import api_key, api_base

def create_transaction(filetype, transaction_type, illiad_request_type, illiad_doc_type, email, pickup, entry):
    
    # Returns a dictionary of transaction templates prepopulated with values from the user arguments.
    # Also returns the title and author for use in the results file.
    if filetype == 'csv':
        transaction_templates = get_transaction_templates_csv(email, pickup, entry, illiad_request_type, illiad_doc_type)
        title = entry.get('Title', '')
        author = entry.get('Author', '')
    elif filetype == 'ris':
        transaction_templates = get_transaction_templates_ris(email, pickup, entry, illiad_request_type, illiad_doc_type)
        title = entry.get('primary_title', '')
        author = entry.get('authors', '')

    # Check if the transaction type is in the transaction_templates_ris dictionary.
    if transaction_type in transaction_templates:

        # If the Type column contains a valid value, return a transaction using the appropriate template.
        # If the file contains a value for a field, use that value. If not, it will be set to ''.
        transaction = {k: entry.get(v, v) for k, v in transaction_templates[transaction_type].items()}
        error = 'No errors'
        return transaction, None, title, author

    # If the Type column contains an invalid value, return an error message and move to the next entry.
    else:
        error = f'The Type field contains an unsupported citation type.'
        return None, error, title, author
    
def process_transaction(filetype, email, filename, filepath, pickup, test_mode):
    
    # Display a message if the program is running in test mode.
    if test_mode:
        print('Running in test mode. Transactions will be included in the results file but not submitted.\n')
    
    print('Processing transactions...\n')

    if filetype == 'ris':
        # Store the citations from the .ris file in a list.
        # Some citations will be mapped to a consistent set of keys used by the transaction templates.
        citations = map_rispy(filepath)
        # print(citations)

    elif filetype == 'csv':
        with open(filepath, 'r', encoding='utf-8') as source_file:
            citations = open_csv(source_file)
            citations = list(citations)
            # print(citations)

    # Get the current date and time.
    now = get_date_time()

    # Ensure the "results" folder exists.
    check_for_results_folder()

    # Construct the results file path.
    results_filepath = construct_results_filepath(filename, now)
    
    # Create a new file for the results.
    with open(results_filepath, 'w', encoding='utf-8', newline='') as resultsfile:
        writer = create_results_file(citations, resultsfile)
        
        # Process a transaction for each entry.
        for i, entry in enumerate(citations, start=1):

            # Initialize the result dictionary.
            result = {
                'Entry number': i, 
                'Title': None, 
                'Author': None, 
                'Error': None, 
                'Transaction': None, 
                'Transaction number': None
            }
            
            # Create a transaction.
            if filetype == 'ris':
                citation_type = entry['type_of_reference']

            elif filetype == 'csv':
                citation_type = str.lower(entry['Item Type'])
            
            transaction_type, illiad_request_type, illiad_doc_type = map_citation_type(citation_type)
            result['Transaction'], result['Error'], result['Title'], result['Author'] = create_transaction(filetype, transaction_type, illiad_request_type, illiad_doc_type, email, pickup, entry)

            # Validate the transaction.
            if not result['Error']:
                result['Error'] = validate_transaction(result['Transaction'])
            
            # If there are any errors, write them to the results file.
            # Transaction will not be submitted if there are errors.
            if result['Error']:
                writer.writerow(result)
                print(f'Entry {i}: ' + result['Error'] + '\n')
                continue
            
            # If no errors at the end of the process, set the error message to 'No errors'.
            if not result['Error']:
                result['Error'] = 'No errors'

            # If in test mode, only append the transaction results to the results file.
            if test_mode:
                writer.writerow(result)
                print(f'Entry {i}: Created the following transaction data: ' + str(result['Transaction']) + '\n')

            # If not in test mode, submit the transaction and append the transaction results to the results file.
            if not test_mode:        
                result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], api_base, api_key, i)
                writer.writerow(result)
                print(f'Entry {i}: Created transaction number {result["Transaction number"]}' + '\n')        
