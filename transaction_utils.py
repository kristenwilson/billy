#!/usr/bin/env python3
# transaction_utils.py
# Description: Utilities to create and process ILLiad transactions; for use by bulk_ill.py.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Custom modules
from transaction_templates import get_transaction_templates_csv, get_transaction_templates_ris
from illiad_api_utils import submit_transaction
from validation_utils import validate_row, validate_transaction
from file_utils import open_csv, open_ris, create_results_file
from rispy_utils import map_rispy

# Configuration
from config import api_key, api_base

# Create a transaction using the .csv template.
# Used by process_transaction_csv.
def create_transaction_csv(transaction_type, email, pickup, row):
    
    # Returns a dictionary of transaction templates prepopulated with values from the user arguments.
    transaction_templates = get_transaction_templates_csv(email, pickup, row)
    
    # Check if the transaction type is in the transaction_templates_csv dictionary.
    if transaction_type in transaction_templates:

        # If the Type column contains a valid value, return a transaction using the appropriate template.
        # If the column contains a value, use that value. If not, the field will be set to ''.
        transaction = {k: row.get(v, v) for k, v in transaction_templates[transaction_type].items()}
        return transaction, None

    # If the Type column contains an invalid value, return an error message and move to the next row.
    else:
        error = f'The Type field must contain either "journalArticle", "book", or "bookSection".'
        return None, error

# Process transactions from a .csv file.
# Used by bulk_ill.py.
def process_transaction_csv(email, filename, filepath, pickup, test_mode):
    
    # Display a message if the program is running in test mode.
    if test_mode:
        print('Running in test mode. Transactions will be included in the results file but not submitted.\n')
    
    print('Processing transactions...\n')

    # Open the file as a CSV reader object.    
    with open(filepath, 'r', encoding='utf-8') as source_file:
        reader = open_csv(source_file)

        # Create a new file for the results.
        with open('results.csv', 'w', encoding= 'utf-8', newline='') as resultsfile:
            writer = create_results_file(reader, resultsfile)
            
            # Create and process a transaction for each row in the reader object.
            for i, row in enumerate(reader, start=1):

                # Initialize the result dictionary. 
                result = {'Line number': i, 'Error': None, 'Transaction': None, 'Transaction number': None}

                # Validate the row.    
                result['Error'] = validate_row(row)
                
                # If there are no errors in the row, create a transaction.
                if not result['Error']:
                    transaction_type = str.lower(row['Item Type'])
                    result['Transaction'], result['Error'] = create_transaction_csv(transaction_type, email, pickup, row)

                # Validate the transaction.
                if not result['Error']:
                    result['Error'] = validate_transaction(result['Transaction'])
                
                # If there are any errors, write them to the results file.
                # The transaction will not be submitted if there are errors.
                if result['Error']:
                    writer.writerow(result)
                    print(f'Row {i}: ' + result['Error'] + '\n')
                    continue
                
                # If in test mode, append transcaytion results to the results file and print them on the screen.
                if test_mode:
                    writer.writerow(result)
                    print(f'Row {i}: Created the following transaction data: ' + str(result['Transaction']) + '\n')

                # If not in test mode, submit the transaction and append transactioin results to the results file.
                if not test_mode:        
                    result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], api_base, api_key, i)
                    writer.writerow(result)
                    print(f'Row {i}: Created transaction number {result["Transaction number"]}' + '\n')

    print('\nProcessing complete.')
    print('Results have been saved to results.csv.\n')

# Create a transaction using the RIS template.
# Used by process_transaction_ris.
def create_transaction_ris(transaction_type, email, pickup, entry):
    
    # Returns a dictionary of transaction templates prepopulated with values from the user arguments.
    transaction_templates = get_transaction_templates_ris(email, pickup, entry)

    # Check if the transaction type is in the transaction_templates_ris dictionary.
    if transaction_type in transaction_templates:

        # If the Type column contains a valid value, return a transaction using the appropriate template.
        # If the .ris file contains a value for a field, use that value. If not, it will be set to ''.
        transaction = {k: entry.get(v, v) for k, v in transaction_templates[transaction_type].items()}
        return transaction, None

    # If the Type column contains an invalid value, return an error message and move to the next row.
    else:
        error = f'The Type field must contain one of the following values: {", ".join(transaction_templates.keys())}'
        return None, error

# Process transactions from a .ris file.
# Used by bulk_ill.py.
def process_transaction_ris(email, filename, filepath, pickup, test_mode):
    
    # Display a message if the program is running in test mode.
    if test_mode:
        print('Running in test mode. Transactions will be included in the results file but not submitted.\n')
    
    print('Processing transactions...\n')

    # Store the entries from the .ris file in a list.
    # Some entries will be mapped to a consistent set of keys used by the transaction templates.
    entries = map_rispy(filepath)

    # Create a new file for the results.
    with open('results.csv', 'w', encoding='utf-8', newline='') as resultsfile:
        writer = create_results_file(entries, resultsfile)
        
        # Create and process a transaction for each entry.
        for i, entry in enumerate(entries, start=1):

            # Initialize the result dictionary.
            result = {'Line number': i, 'Error': None, 'Transaction': None, 'Transaction number': None}

            # TODO: Create a function to validate .ris entries.
            
            # If there are no errors in the entry, create a transaction.
            transaction_type = entry['type_of_reference']
            result['Transaction'], result['Error'] = create_transaction_ris(transaction_type, email, pickup, entry)

            # Validate the transaction.
            if not result['Error']:
                result['Error'] = validate_transaction(result['Transaction'])
            
            # If there are any errors, write them to the results file.
            # Transaction will not be submitted if there are errors.
            if result['Error']:
                writer.writerow(result)
                print(f'Row {i}: ' + result['Error'] + '\n')
                continue
            
            # If in test mode, append the transaction results to the results file.
            if test_mode:
                writer.writerow(result)
                print(f'Row {i}: Created the following transaction data: ' + str(result['Transaction']) + '\n')

            # If not in test mode, submit the transaction and append the transaction results to the results file.
            if not test_mode:        
                result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], api_base, api_key, i)
                writer.writerow(result)
                print(f'Row {i}: Created transaction number {result["Transaction number"]}' + '\n')