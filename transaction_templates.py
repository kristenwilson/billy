#!/usr/bin/env python3
# transaction_templates.py
# Description: Templates to create ILLiad transactions; for use by bulk_ill.py.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu


# Map CSV citation types to types used by transaction templates.
def map_csv_type(citation_type):
    if citation_type == 'journalarticle' or citation_type == 'newspaperarticle' or citation_type == 'magazinearticle' or citation_type == 'encyclopediaarticle':
        return 'journalarticle'
    elif citation_type == 'booksection':
        return 'booksection'
    elif citation_type == 'book':
        return 'book'
    elif citation_type == 'thesis':
        return 'thesis'
    elif citation_type == 'conferencepaper':
        return 'conferencepaper'
    else:
        return None

# Create a dictionary of transaction templates prepopulated with values from the user arguments and .csv file.
# The .csv template uses custom field names.
# If no value is provided, the field will be set to ''.
# Used by create_transaction_csv.
def get_transaction_templates_csv(email, pickup, row):
    return {
     'journalarticle': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'DocumentType': 'Article',
        'PhotoJournalTitle': row.get('Publication Title', ''),
        'PhotoArticleTitle': row.get('Title', ''),
        'PhotoArticleAuthor': row.get('Author', ''),
        'PhotoJournalVolume': row.get('Volume', ''),
        'PhotoJournalIssue': row.get('Issue', ''),
        'PhotoJournalYear': row.get('Publication Year', ''),    
        'PhotoJournalInclusivePages': row.get('Pages', ''),
        'DOI': row.get('DOI', ''),
        'ISSN': row.get('ISSN', '')
    },
    'book': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'DocumentType': 'Book',
        'LoanTitle': row.get('Title', ''),
        'LoanAuthor': row.get('Author', ''),
        'LoanDate': row.get('Publication Year', ''),
        'ISSN': row.get('ISBN', ''),
        'LoanPublisher': row.get('Publisher', ''),
    },
    'booksection': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'DocumentType': 'Book Chapter',
        'PhotoJournalTitle': row.get('Publication Title', ''),
        'PhotoArticleTitle': row.get('Title', ''),
        'PhotoArticleAuthor': row.get('Author', ''),
        'PhotoJournalVolume': row.get('Volume', ''),
        'PhotoJournalIssue': row.get('Issue', ''),
        'PhotoJournalYear': row.get('Publication Year', ''),    
        'PhotoJournalInclusivePages': row.get('Pages', ''),
        'DOI': row.get('DOI', ''),
        'ISSN': row.get('ISBN', '')
    },
        'thesis': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'DocumentType': 'Thesis',
        'LoanTitle': row.get('Title', ''),
        'LoanAuthor': row.get('Author', ''),
        'LoanDate': row.get('Publication Year', ''),
        'ISSN': row.get('ISBN', ''),
        'LoanPublisher': row.get('Publisher', ''),
    },
        'conferencepaper': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'DocumentType': 'Article',
        'PhotoJournalTitle': row.get('Conference Name', ''),
        'PhotoArticleTitle': row.get('Title', ''),
        'PhotoArticleAuthor': row.get('Author', ''),
        'PhotoJournalVolume': row.get('Volume', ''),
        'PhotoJournalIssue': row.get('Issue', ''),
        'PhotoJournalYear': row.get('Publication Year', ''),    
        'PhotoJournalInclusivePages': row.get('Pages', ''),
        'DOI': row.get('DOI', ''),
        'ISSN': row.get('ISSN', '')
    },
}

# Map RIS citation types to types used by transaction templates.
def map_ris_type(citation_type):
    if citation_type == 'JOUR' or citation_type == 'EJOUR' or citation_type == 'MGZN' or citation_type == 'NEWS' or citation_type == 'ENCYC' or citation_type == 'CONF' or citation_type == 'CPAPER':
        return 'JOUR'
    elif citation_type == 'CHAP':
        return 'CHAP'
    elif citation_type == 'BOOK':
        return 'BOOK'
    elif citation_type == 'THES':
        return 'THES'
    else:
        return None

# Create a dictionary of transaction templates prepopulated with values from the user arguments and .ris file.
# The .ris template uses a simplified set of RIS field names. Field names are mapped to the template keys using the map_rispy function.
# If no value is provided, the field will be set to ''.
# Used by create_transaction_ris.
def get_transaction_templates_ris(email, pickup, entry):
    return {
        'JOUR': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'DocumentType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': entry.get('secondary_title', ''),
        'PhotoArticleTitle': entry.get('primary_title', ''),
        'PhotoArticleAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'PhotoJournalYear': entry.get('year', ''),
        'PhotoJournalInclusivePages': entry.get('start_page', '') + '-' + entry.get('end_page', ''),
        'PhotoItemPublisher': entry.get('publisher', ''),
        'PhotoItemPlace': entry.get('place_published', ''),
        'DOI': entry.get('doi', ''),
        'ISSN': entry.get('issn', '')
    },
     'CHAP': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'DocumentType': 'Book Chapter',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': entry.get('secondary_title', ''),
        'PhotoArticleTitle': entry.get('primary_title', ''),
        'PhotoArticleAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'PhotoJournalVolume': entry.get('volume', ''),
        'PhotoJournalIssue': entry.get('number', ''),  
        'PhotoJournalYear': entry.get('year', ''),   
        'PhotoJournalInclusivePages': entry.get('start_page', '') + '-' + entry.get('end_page', ''),
        'PhotoItemPublisher': entry.get('publisher', ''),
        'PhotoItemPlace': entry.get('place_published', ''),
        'DOI': entry.get('doi', ''),
        'ISSN': entry.get('issn', ''),
    },
    'BOOK': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'DocumentType': 'Book',
        'LoanTitle': entry.get('primary_title', ''),
        'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'LoanDate': entry.get('year', ''),
        'LoanPublisher': entry.get('publisher', ''),
        'ISSN': entry.get('issn', ''),
    },
    'THES': {
        'ExternalUserId': email,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'DocumentType': 'Thesis',
        'LoanTitle': entry.get('primary_title', ''),
        'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'LoanDate': entry.get('year', ''),
        'LoanPublisher': entry.get('publisher', ''),
    },
}