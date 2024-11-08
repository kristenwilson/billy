#!/usr/bin/env python3
# transaction_templates.py
# Description: Templates to create ILLiad transactions
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

import yaml

# Map citation types to types used by transaction templates.
def map_citation_type(citation_type):
    # Load the citation types from the YAML file
    with open('citation_types.yaml', 'r', encoding='utf-8') as file:
        citation_types = yaml.safe_load(file)

    for type in citation_types:
        ris_types = str.lower(type.get('ris_type', ''))
        zotero_types = str.lower(type.get ('zotero_type', ''))

        if str.lower(citation_type) in ris_types or citation_type in zotero_types:
            return type['transaction_template'], type['illiad_request_type'], type['illiad_doc_type']
            
    # Return None if no match is found
    return None, None, None

# Create a transaction template prepopulated with values from the user arguments and .csv file.
# If no value is provided, the field will be set to ''.
def get_transaction_templates_csv(email, pickup, row, illiad_request_type, illiad_doc_type):
    return {
     'JOUR': {
        'ExternalUserId': email,
        'RequestType': illiad_request_type,
        'ProcessType': 'Borrowing',
        'DocumentType': illiad_doc_type,
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
        'RequestType': illiad_request_type,
        'ProcessType': 'Borrowing',
        'DocumentType': illiad_doc_type,
        'LoanTitle': row.get('Title', ''),
        'LoanAuthor': row.get('Author', ''),
        'LoanDate': row.get('Publication Year', ''),
        'ISSN': row.get('ISBN', ''),
        'LoanPublisher': row.get('Publisher', ''),
    },
    'CHAP': {
        'ExternalUserId': email,
        'RequestType': illiad_request_type,
        'ProcessType': 'Borrowing',
        'DocumentType': illiad_doc_type,
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
        'RequestType': illiad_request_type,
        'ProcessType': 'Borrowing',
        'DocumentType': illiad_doc_type,
        'LoanTitle': row.get('Title', ''),
        'LoanAuthor': row.get('Author', ''),
        'LoanDate': row.get('Publication Year', ''),
        'ISSN': row.get('ISBN', ''),
        'LoanPublisher': row.get('Publisher', ''),
    },
        'CONF': {
        'ExternalUserId': email,
        'RequestType': illiad_request_type,
        'ProcessType': 'Borrowing',
        'DocumentType': illiad_doc_type,
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

# Create a transaction templates prepopulated with values from the user arguments and .ris file.
# The .ris template uses a simplified set of RIS field names. Field names are mapped to the template keys using the map_rispy function.
# If no value is provided, the field will be set to ''.
def get_transaction_templates_ris(email, pickup, entry, illiad_requst_type, illiad_doc_type):
    return {
        'JOUR': {
        'ExternalUserId': email,
        'RequestType': illiad_requst_type,
        'DocumentType': illiad_doc_type,
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
        'RequestType': illiad_requst_type,
        'DocumentType': illiad_doc_type,
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
        'RequestType': illiad_requst_type,
        'ProcessType': 'Borrowing',
        'DocumentType': illiad_doc_type,
        'LoanTitle': entry.get('primary_title', ''),
        'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'LoanDate': entry.get('year', ''),
        'LoanPublisher': entry.get('publisher', ''),
        'ISSN': entry.get('issn', ''),
    },
    'THES': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': illiad_requst_type,
        'ProcessType': 'Borrowing',
        'DocumentType': illiad_doc_type,
        'LoanTitle': entry.get('primary_title', ''),
        'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'LoanDate': entry.get('year', ''),
        'LoanPublisher': entry.get('publisher', ''),
    },
    'CONF': {
        'ExternalUserId': email,
        'RequestType': illiad_requst_type,
        'DocumentType': illiad_doc_type,
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