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
    args = parser.parse_args()
    
    # Assign command line arguments to variables
    filename = args.filename
    email = args.email
    return email, filename

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
        print('User ' + email + ' confirmed.\n')
    
    else:
        print(str(response.status_code) + ': ' + response.json()['Message'] + '\n')
        sys.exit()

def submit_transaction(transaction):
    # Create a transaction in ILLiad for each row in the file.
    api_url = api_base + '/Transaction/'
    headers = {'ContentType': 'application/json', 'ApiKey': api_key}

    response = requests.post(api_url, headers=headers, json=transaction)
    if response.status_code == 200:
        print(str(response.json()['TransactionNumber']))

    else:
        print(str(response.status_code) + ': ' + response.json()['Message'] + '\n')

def create_transaction_csv(email, filename, filepath):

     # Open the file as a CSV reader object.
    print('Reading file ' + filename + '...\n')
    
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        print('Creating transactions...\n')

        # Create and submit a transaction for each row in the reader object.
        for row in reader:   

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

    print('\nProcessing complete.')
        
#TODO: def create_transaction_ris(email, filename, filepath):

def main():
    email, filename = get_args()
    filepath = check_file(filename)
    check_user(email)
    create_transaction_csv(email, filename, filepath)

if __name__ == '__main__':
    main()