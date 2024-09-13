#!/usr/bin/env python3
# transaction_templates.py
# Description: Templates to create ILLiad transactions; for use by bulk_ill.py.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Maps citation types the types used by transaction_templates.py.
type_mapping = {
        'JOUR': ['JOUR', 'EJOUR', 'MGZN', 'NEWS', 'ENCYC', 'CPAPER', 'GEN', 'ELEC', 'SLIDE', 'journalarticle', 'newspaperarticle', 'magazinearticle', 'encyclopediaarticle', 'webpage,' 'slide'],
        'CHAP': ['CHAP', 'booksection'],
        'BOOK': ['BOOK', 'book'],
        'THES': ['THES', 'thesis'],
        'CONF': ['CONF', 'conferencepaper']
    }

# Map citation types to types used by transaction templates.
def map_citation_type(citation_type):
    for key, values in type_mapping.items():
            if citation_type in values:
                return key
    return None

# Create a dictionary of transaction templates prepopulated with values from the user arguments and .csv file.
# The .csv template uses custom field names.
# If no value is provided, the field will be set to ''.
# Used by create_transaction_csv.
def get_transaction_templates_csv(email, pickup, row):
    return {
     'JOUR': {
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
    'BOOK': {
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
    'CHAP': {
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
        'THES': {
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
        'CONF': {
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
        'PhotoJournalVolume': entry.get('volume', ''),
        'PhotoJournalIssue': entry.get('number', ''),
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
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'DocumentType': 'Thesis',
        'LoanTitle': entry.get('primary_title', ''),
        'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'LoanDate': entry.get('year', ''),
        'LoanPublisher': entry.get('publisher', ''),
    },
    'CONF': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'DocumentType': 'Article',
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
        'ISSN': entry.get('issn', '')
    },
}