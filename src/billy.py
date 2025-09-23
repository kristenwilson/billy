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

from rispy_mapping import map_rispy
from transaction_templates import map_citation_type

from config import api_key, api_base, pickup_locations
from file_utils import validate_file, read_csv
from api import check_user, submit_transaction
from transaction import create_transaction, validate_transaction
from exceptions import BillyError

# Configure logging to output to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("billy.log"),
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
                        choices=pickup_locations,
                        default='')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run the script in test mode to output a report showing which transactions will be created and which will produce errors.')
    args = parser.parse_args()    
    
    logging.info(f'Arguments: email={args.email}, filename={args.filename}, pickup={args.pickup}, test_mode={args.test}')
    return args.email, args.filename, args.pickup, args.test


def process_transaction(filetype, email, filename, filepath, pickup, test_mode, messages):
    # Display a message if the program is running in test mode.
    if test_mode:
        messages.append('Running in test mode. Transactions will be included in the results file but not submitted.\n')
    
    # Get the current date and time to the nearest second for use in filename
    # now = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

    # Ensure the "test/data/actual" folder exists
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test', 'data', 'actual'))
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Construct the filepath for the results file
    base_filename = os.path.splitext(filename)[0]
    results_filename = f'{base_filename}_actual.csv'
    results_filepath = os.path.join(results_dir, results_filename)
    messages.append(f'Results saved to {results_filepath}\n')

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
            citations = list(read_csv(filepath))
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

            logging.info(f"Transaction: {result['Transaction']}")

            # Validate the transaction.
            if not result['Error']:
                result['Error'] = validate_transaction(result['Transaction'])

            logging.info(f"Errors: {result['Error']}")
            
            # If there are any errors, write them to the results file.
            # Transaction will not be submitted if there are errors.
            if result['Error']:
                writer.writerow(result)
                messages.append(f'Entry {i}: ' + result['Error'] + '\n')
                continue
            
            # If no errors at the end of the process, set the error message to 'No errors'.
            if not result['Error']:
                result['Error'] = 'No errors'

                # If in test mode, only append the transaction results to the results file.
                if test_mode:
                    result['Transaction number'] = 'n/a'
                    writer.writerow(result)
                    messages.append(f'Entry {i}: Created the following transaction data: ' + str(result['Transaction']) + '\n')
                    logging.info(f"Transaction submitted: {result['Transaction number']}")

                # If not in test mode, submit the transaction and append the transaction results to the results file.
                if not test_mode:        
                    result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], api_base, api_key, i)
                    writer.writerow(result)
                    messages.append(f'Entry {i}: Created transaction number {result["Transaction number"]}' + '\n')

def main(email=None, filename=None, pickup=None, test_mode=None):
    
    messages = []
    
    logging.info('Processing initiated')
    
    try:
        # Get command line arguments
        if email is None or filename is None or pickup is None or test_mode is None:
            email, filename, pickup, test_mode = get_args()
        
        # Validate the file and user.
        filepath, filetype, messages = validate_file(filename, messages)
        messages = check_user(email, api_base, api_key, messages)
        
        # Process the file
        process_transaction(filetype, email, filename, filepath, pickup, test_mode, messages)
    
    except BillyError as e:
        messages.append(str(e))
        logging.error(str(e))

    except Exception as e:
        messages.append(f'Unexpected error: {str(e)}')
        logging.error(f'Unexpected error: {str(e)}')

    for message in messages:
        print(message)

    if any('Error' for message in messages):
        sys.exit()

if __name__ == '__main__':
    main()