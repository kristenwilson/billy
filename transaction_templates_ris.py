def get_transaction_templates(email, pickup, entry):
    return {
        'JOUR': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': entry.get('secondary_title', ''),
        'PhotoArticleTitle': entry.get('title', ''),
        'PhotoArticleAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'PhotoJournalYear': entry.get('year', ''),   
        'PhotoJournalInclusivePages': entry.get('start_page', '') + '-' + entry.get('end_page', ''),
    },
     'CHAP': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': entry.get('secondary_title', ''),
        'PhotoArticleTitle': entry.get('title', ''),
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
        'LoanTitle': entry.get('title', ''),
        'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
        'LoanDate': entry.get('year', ''),
    }
}