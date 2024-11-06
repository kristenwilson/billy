#!/usr/bin/env python3
# billy.py
# Bulk ILL, Yall! (Billy)
# Description: This script processes citations from a .csv or .ris file and creates interlibrary loan transactions in ILLiad for each citation.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Python modules
import argparse
import os
import sys
import csv
import requests
import datetime

# Custom modules
from rispy_mapping import map_rispy
from transaction_templates import map_citation_type, get_transaction_templates_csv, get_transaction_templates_ris

# Configuration
from config import api_key, api_base
     
def get_args():
    
    # Identify required inputs via command line arguments.
    parser = argparse.ArgumentParser(description='Create interlibrary loan transactions in ILLiad for articles in a csv file.')
    parser.add_argument('email', 
                        help='The email address of the person who will receive the requested materials. This person must already have a user account in ILLiad.')
    parser.add_argument('filename', 
                        help='The name of the file to be read. Must be a .csv file.')
    parser.add_argument('-p', '--pickup', 
                        help='The library where the requested materials will be picked up. This is only needed if you are requesting physical materials.',
                        choices=['Hill', 'Hunt', 'Design', 'Natural Resources', 'Veterinary Medicine', 'Textiles', 'METRC', 'Distance/Extension'],
                        default='')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run the script in test mode to output a report showing which transactions will be created and which will produce errors.')
    args = parser.parse_args()    
    
    return args.email, args.filename, args.pickup, args.test

def validate_file(filename):

    # Get the filepath of the user's file.
    script_dir = os.path.join(os.path.dirname(__file__), 'data_files')
    filepath = os.path.join(script_dir, filename)

    # If the file doesn't exist, exit the script.
    if not os.path.isfile(filepath):
        print('Error: The file ' + filepath + ' does not exist.\n')
        sys.exit()

    # Verify that the file is either a RIS or CSV file.
    filetype = None    
    with open(filepath, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip()
        
        # Skip blank lines at the beginning of the file.
        while not first_line:
            first_line = file.readline().strip()
        
        # If the first line of the file is a RIS 'type' tag, the file is treated as an RIS file.
        if first_line.__contains__('TY  -'):
            filetype = 'ris'
            print('\nRIS file confirmed.')
        
        # If there is a comma in the first line, the file is treated as a CSV file.
        elif ',' in first_line:        
            try:
                with open(filepath, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Check that the file contains an 'Item Type' column and if not, exit the script.
                    if 'Item Type' not in reader.fieldnames:
                        print('Error: The file must contain a column called "Item Type".\n')
                        sys.exit()

                    filetype = 'csv'
                    print('\nCSV file confirmed.')
            
            # If the file is not a valid CSV file, exit the script.
            except csv.Error:
                print('Error: The file ' + filepath + ' is not a valid CSV file.\n')
                sys.exit()
            
        # If the file is not a valid RIS or CSV file, exit the script.
        else:
            print('Error: The file ' + filename + ' is not a valid file type. The file must be a CSV or RIS file.\n')
            sys.exit()

        return filepath, filetype
    
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

def validate_transaction(transaction):
            
    # Check that the transaction contains all required fields.
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
        error = f'The following required fields are missing from the transaction: {", ".join(missing_fields)}.'
        return error

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

def process_transaction(filetype, email, filename, filepath, pickup, test_mode):
    # Display a message if the program is running in test mode.
    if test_mode:
        print('Running in test mode. Transactions will be included in the results file but not submitted.\n')
    
    print('Processing transactions...\n')

    # Store the citations from the file in a list.
    # RIS citations will be mapped to a consistent set of keys used by the transaction templates.
    if filetype == 'ris':
        citations = map_rispy(filepath)
    elif filetype == 'csv':
        with open(filepath, 'r', encoding='utf-8') as source_file:
            citations = csv.DictReader(source_file)
            citations = list(citations)

    # Get the current date and time to the nearest second for use in filename
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

    # Ensure the "results" folder exists
    if not os.path.exists('results'):
        os.makedirs('results')

    # Construct the filepath for the results file
    results_filename = f'{filename}_{now}.csv'
    results_filepath = os.path.join('results', results_filename)
    print(f'Results will be saved to {results_filepath}\n')

    # Create a new file for the results.
    with open(results_filepath, 'w', encoding='utf-8', newline='') as resultsfile:
        writer = None
        # Create a header row for the results file.
        fieldnames = ['Entry number', 'Title', 'Author', 'Error', 'Transaction', 'Transaction number']
        writer = csv.DictWriter(resultsfile, fieldnames=fieldnames)
        writer.writeheader()

        # Initialize the result dictionary.
        result = {
        'Entry number': None, 
        'Title': None, 
        'Author': None, 
        'Error': None, 
        'Transaction': None, 
        'Transaction number': None
        }

        # Process a transaction for each entry.
        for i, entry in enumerate(citations, start=1):
        
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
        
def main():
    # Get command line arguments
    email, filename, pickup, test_mode = get_args()
    
    # Validate that the file and user.
    filepath, filetype = validate_file(filename)
    check_user(email, api_base, api_key)
    
    # Process the file
    process_transaction(filetype, email, filename, filepath, pickup, test_mode)

    print('\nProcessing complete.')

if __name__ == '__main__':
    main()