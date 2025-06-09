#!/usr/bin/env python3
# billy.py
# Bulk ILL, Yall! (Billy)
# Description: This script processes citations from a .csv or .ris file and creates interlibrary loan transactions in ILLiad for each citation.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

import argparse
import os
import sys
import csv
import requests
import datetime
import logging
import json

from rispy_mapping import map_rispy
from transaction_templates import map_citation_type, get_transaction_templates_csv, get_transaction_templates_ris

from config import api_key, api_base

class BillyError(Exception):
    pass

# Configure logging to output to a file
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("billy.log"),
        logging.StreamHandler(sys.stdout)
    ]
)     
def get_args():
    
    # Identify required inputs via command line arguments.
    parser = argparse.ArgumentParser(description='Create interlibrary loan transactions in ILLiad for articles in a CSV or RIS file.')
    parser.add_argument('email', 
                        help='The email address of the person who will receive the requested materials. This person must already have a user account in ILLiad.')
    parser.add_argument('filename', 
                        help='The name of the file to be read. Must be a .csv or .ris file.')
    parser.add_argument('-p', '--pickup', 
                        help='The library where the requested materials will be picked up. This is only needed if you are requesting physical materials.',
                        choices=['Hill', 'Hunt', 'Design', 'Natural Resources', 'Veterinary Medicine', 'Textiles', 'METRC', 'Distance/Extension'],
                        default='')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run the script in test mode to output a report showing which transactions will be created and which will produce errors.')
    args = parser.parse_args()    
    
    logging.info(f'Arguments: email={args.email}, filename={args.filename}, pickup={args.pickup}, test_mode={args.test}')
    return args.email, args.filename, args.pickup, args.test

def validate_file(filename, messages):

    # Construct the filepath of the user's file.
    script_dir = os.path.join(os.path.dirname(__file__), 'data_files')
    filepath = os.path.join(script_dir, filename)

    # If the file doesn't exist, raise an error.
    if not os.path.isfile(filepath):
        error_message = ('The file ' + filepath + ' does not exist.\n')
        logging.error(error_message)
        raise BillyError(error_message)

    # Verify that the file is either a RIS or CSV file.
    filetype = None    
    with open(filepath, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip()
        
        # Skip blank lines at the beginning of the file.
        while not first_line:
            first_line = file.readline().strip()
            if not first_line:
                # Check if the file is empty
                if file.tell() == 0:
                    error_message = 'The file is empty.'
                    logging.error(error_message)
                    raise BillyError(error_message)
        
        # If the first line of the file is a RIS 'type' tag, the file is treated as an RIS file.
        if first_line.__contains__('TY  -'):
            filetype = 'ris'
            success_message = 'RIS file confirmed.'
            #messages.append(('success', success_message))
            logging.info(success_message)
        
        # If there is a comma in the first line, the file is treated as a CSV file.
        elif ',' in first_line:        
            try:
                with open(filepath, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Check that the file contains an 'Item Type' column and if not, raise an error.
                    if 'Item Type' not in reader.fieldnames:
                        error_message = 'The file must contain a column called "Item Type".\n'
                        logging.error(error_message)
                        raise BillyError(error_message)
                    
                    else:
                        filetype = 'csv'
                        success_message = 'CSV file confirmed.'
                        #messages.append(('success', success_message))
                        logging.info(success_message)
            
            # If the file is not a valid CSV file, raise an error.
            except csv.Error:
                error_message = ('The file ' + filepath + ' is not a valid CSV file.\n')
                logging.error(error_message)
                raise BillyError(error_message)
            
        # If the file is not a valid RIS or CSV file, raise an error.
        else:
            error_message = 'The file ' + filename + ' is not a valid file type. The file must be a CSV or RIS file.\n'
            logging.error(error_message)
            raise BillyError(error_message)

        return filepath, filetype
    
def check_user(email, api_base, api_key, messages):

    # Define the API URL and headers.
    api_url = api_base + '/Users/ExternalUserID/' + email
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    try:
        # Make the API request.
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            # If the user has a "Cleared" status of "Yes", the user is valid.
            if response.json()['Cleared'] == 'Yes':
                success_message = 'User ' + email + ' confirmed.'
                #messages.append(('success', success_message))
                logging.info(success_message)
                return messages
            # If the user has a "Cleared" status of "No", the user is not valid.
            elif response.json()['Cleared'] == 'No': 
                error_message = '\nUser ' + email + ' is not cleared to place requests.\n'
                logging.error(error_message)
                raise BillyError(error_message)
        
        # Raise an error if the API key is not valid.
        elif response.status_code == 401:
            error_message = 'Invalid API key. Please check the API credentials in config.py.\n'
            logging.error(error_message)
            raise BillyError(error_message)
        
        # Print any other errors.
        else:
            error_message = response.json()['Message'] + '\n'
            logging.error(error_message)
            raise BillyError(error_message)
        
    except Exception as e:
        logging.error(e)
        raise BillyError(e)

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
        error_message = f'The following required fields are missing from the transaction: {", ".join(missing_fields)}.'
        return error_message

def submit_transaction(transaction, api_base, api_key, i):
    
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
            error = (f'Error on line {i}: ' + str(response.status_code) + ': ' + response.json()['Message'] + '\n')
            return None, error
    
    # Print any errors related to the API request.
    except Exception as e:
        error = (f'Error on line {i}: ' + str(e) + '\n')
        logging.error(error)
        return None, error

def process_transaction(filetype, email, filename, filepath, pickup, test_mode, messages):
    # Display a message if the program is running in test mode.
    if test_mode:
        messages.append(('info', 'Running in test mode. Transactions will be included in the results file but not submitted.'))
    
    # Get the current date and time to the nearest second for use in filename
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

    # Ensure the "results" folder exists
    if not os.path.exists('static/results'):
        os.makedirs('static/results')

    # Construct the filepath for the results file
    results_filename = f'{filename}_{now}.csv'
    results_filepath = os.path.join('static/results', results_filename)
    info_message = f'Results saved to {results_filepath}'
    #messages.append(('info', info_message))
    logging.info(info_message)

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

        # Store the citations from the file in a list.
        # RIS citations will be mapped to a consistent set of keys used by the transaction templates.
        if filetype == 'ris':
            citations = map_rispy(filepath)
        elif filetype == 'csv':
            with open(filepath, 'r', encoding='utf-8') as source_file:
                citations = csv.DictReader(source_file)
                citations = list(citations)

        # Process a transaction for each entry.
        for i, entry in enumerate(citations, start=1):
        
            # Get the citation type from the source file.
            if filetype == 'ris':
                citation_type = entry['type_of_reference']
            elif filetype == 'csv':
                citation_type = str.lower(entry['Item Type'])
            
            # Map the transaction type from the input file to the standardized values.
            transaction_type, illiad_request_type, illiad_doc_type = map_citation_type(citation_type)

            # Create the transaction based on the transaction type.
            result['Transaction'], result['Error'], result['Title'], result['Author'] = create_transaction(filetype, transaction_type, illiad_request_type, illiad_doc_type, email, pickup, entry)

            # Validate the transaction.
            if not result['Error']:
                result['Error'] = validate_transaction(result['Transaction'])

            # If there are any errors, write them to the results file.
            # Transaction will not be submitted if there are errors.
            if result['Error']:
                writer.writerow(result)
                error_message = f"Entry {i}: {result['Error']} ({result['Title']})"
                messages.append(('error', error_message))
                logging.info(error_message)
                continue
            
            # If no errors at the end of the process, set the error message to 'No errors'.
            if not result['Error']:
                result['Error'] = 'No errors'

                # If in test mode, only append the transaction results to the results file.
                if test_mode:
                    result['Transaction number'] = 'n/a'
                    writer.writerow(result)
                    success_message = f'Entry {i}: Created the following transaction data: ' + str(result['Transaction'])
                    messages.append(('success', success_message))
                    logging.info(success_message)

                # If not in test mode, submit the transaction and append the transaction results to the results file.
                if not test_mode:        
                    result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], api_base, api_key, i)
                    writer.writerow(result)
                    success_message = f'Entry {i}: Created transaction number {result["Transaction number"]}' + '\n'
                    messages.append(('success', success_message))
                    logging.info(success_message)
    return results_filename

def main(email=None, filename=None, pickup=None, test_mode=None):
    
    messages = []
    
    logging.info('Processing initiated')
    
    try:
        # Get command line arguments
        if email is None or filename is None or pickup is None or test_mode is None:
            email, filename, pickup, test_mode = get_args()
        
        # Validate the file and user.
        filepath, filetype = validate_file(filename, messages)
        check_user(email, api_base, api_key, messages)
        
        # Process the file
        results_filename = process_transaction(filetype, email, filename, filepath, pickup, test_mode, messages)

    except Exception as e:
        messages.append(('error', f'Error: {str(e)}'))
        logging.error(('error', f'Error: {str(e)}'))

    for category, message in messages:
        print(f'{category.upper()} {message}\n')

    return messages, results_filename

if __name__ == '__main__':
    main()