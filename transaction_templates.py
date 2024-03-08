def get_transaction_templates(email, pickup, row):
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