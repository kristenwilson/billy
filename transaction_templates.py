#!/usr/bin/env python3
# transaction_templates.py
# Description: Templates to create ILLiad transactions; for use by bulk_ill.py.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Create a dictionary of transaction templates prepopulated with values from the user arguments and .csv file.
# The .csv template uses custom field names.
# If no value is provided, the field will be set to ''.
# Used by create_transaction_csv.
def get_transaction_templates_csv(email, pickup, row):
    return {
     'article': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': row.get('Journal title', ''),
        'PhotoArticleTitle': row.get('Article title', ''),
        'PhotoArticleAuthor': row.get('Author', ''),
        'PhotoJournalVolume': row.get('Volume', ''),
        'PhotoJournalIssue': row.get('Issue', ''),
        'PhotoJournalYear': row.get('Year', ''),    
        'PhotoJournalInclusivePages': row.get('Pages', ''),
        'DOI': row.get('DOI', ''),
        'ISSN': row.get('ISSN/ISBN', '')
    },
    'book': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'LoanTitle': row.get('Book title', ''),
        'LoanAuthor': row.get('Author', ''),
        'LoanDate': row.get('Publication date', ''),
        'ISSN': row.get('ISSN/ISBN', ''),
        'LoanPublisher': row.get('Publisher', ''),
    }
}

# Create a dictionary of transaction templates prepopulated with values from the user arguments and .ris file.
# The .ris template uses a simplified set of RIS field names. Field names are mapped to the template keys using the map_rispy function.
# If no value is provided, the field will be set to ''.
# Used by create_transaction_ris.
def get_transaction_templates_ris(email, pickup, entry):
    return {
        'JOUR': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': entry.get('secondary_title', ''),
        'PhotoArticleTitle': entry.get('primary_title', ''),
        'PhotoArticleAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'PhotoJournalYear': entry.get('year', ''),
        'PhotoJournalInclusivePages': entry.get('start_page', '') + '-' + entry.get('end_page', ''),
    },
     'CHAP': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': entry.get('secondary_title', ''),
        'PhotoArticleTitle': entry.get('primary_title', ''),
        'PhotoArticleAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'PhotoJournalVolume': entry.get('volume', ''),
        'PhotoJournalIssue': entry.get('number', ''),  
        'PhotoJournalYear': entry.get('year', ''),   
        'PhotoJournalInclusivePages': entry.get('start_page', '') + '-' + entry.get('end_page', ''),
        'DOI': entry.get('doi', ''),
    },
    'BOOK': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'LoanTitle': entry.get('primary_title', ''),
        'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'LoanDate': entry.get('year', ''),
    }
}