#!/usr/bin/env python3
# bulk_ill.py
# Purpose: Input citations from a .csv file and create interlibrary loan transactions in ILLiad for each citation.
# Author: Kristen Wilson, NC State Libraries

import os.path
import sys
import argparse
import csv
import requests
import rispy
from config import api_key, api_base

def get_args():
    
    # Identify required inputs via command line arguments
    parser = argparse.ArgumentParser(description='Create interlibrary loan transactions in ILLiad for articles in a csv file.')
    parser.add_argument('email', help='The email address of the person who will receive the requested materials. This person must already have a user account in ILLiad.')
    parser.add_argument('filename', help='The name of the file to be read. Must be a .csv file.')
    parser.add_argument('-p', '--pickup', help='The library where the requested materials will be picked up. This is only needed if you are requesting physical materials.')
    args = parser.parse_args()
    
    # Assign command line arguments to variables
    filename = args.filename
    email = args.email
    if args.pickup:
        pickup = args.pickup
    else:
        pickup = ''
    
    return email, filename, pickup

def check_file(filename):

    # Check that the file exists in the data_files directory. 
    script_dir = os.path.join(os.path.dirname(__file__), 'data_files')
    filepath = os.path.join(script_dir, filename)

    if not os.path.isfile(filepath):
        print('Error: The file ' + filepath + ' does not exist.\n')
        sys.exit()

    else:
        return filepath

def check_user(email):

    # Check that the email address is associated with a valid user account in ILLiad.
    api_url = api_base + '/Users/ExternalUserID/' + email
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        print('\nUser ' + email + ' confirmed.\n')
    
    else:
        print(str(response.status_code) + '\n: ' + response.json()['Message'] + '\n')
        sys.exit()

def submit_transaction(transaction):
    
    # Submit transaction data to the ILLiad API.
    api_url = api_base + '/Transaction/'
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    response = requests.post(api_url, headers=headers, json=transaction)
    if response.status_code == 200:
        print(str(response.json()['TransactionNumber']))

    else:
        print(str(response.status_code) + ': ' + response.json()['Message'] + '\n')

def process_transaction_csv(email, filename, filepath, pickup):

     # Open the file as a CSV reader object.
    print('Reading file ' + filename + '...\n')
    
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        print('Creating transactions...\n')

        # Create and submit a transaction for each row in the reader object.
        for row in reader:

            # Define transaction fields for article requests.
            if str.lower(row['Type']) == ('article'):
                transaction = {
                    'ExternalUserId': email,
                    'RequestType': 'Article',
                    'ProcessType': 'Borrowing',
                    'PhotoJournalTitle': row['Journal title'],
                    'PhotoArticleTitle': row['Title'],
                    'PhotoArticleAuthor': row['Author'],
                    'PhotoJournalVolume': row['Volume'],
                    'PhotoJournalIssue': row['Issue'],
                    'PhotoJournalYear': row['Year'],    
                    'PhotoJournalInclusivePages': row['Pages'],
                    'DOI': row['DOI'],
                }

                submit_transaction(transaction)

            # Define transaction fields for book requests.
            elif str.lower(row['Type']) == ('book'):
                transaction = {
                    'ExternalUserId': email,
                    'ItemInfo4': pickup,
                    'RequestType': 'Loan',
                    'ProcessType': 'Borrowing',
                    'LoanTitle': row['Title'],
                    'LoanAuthor': row['Author'],
                    'LoanDate': row['Date'],
                }

                submit_transaction(transaction)

            # If the Type column contains an invalid value, print an error message and exit the script.
            else:
                print('Error: The Type column must contain either "article" or "book".\n')
                sys.exit()

    print('\nProcessing complete.')
        
#TODO: def create_transaction_ris(email, filename, filepath):

def main():
    email, filename, pickup = get_args()
    filepath = check_file(filename)
    check_user(email)
    process_transaction_csv(email, filename, filepath, pickup)

if __name__ == '__main__':
    main()