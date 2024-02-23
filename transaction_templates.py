def get_transaction_templates(email, pickup, row):
    return {
     'article': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': row.get('Journal title', 'Unknown'),
        'PhotoArticleTitle': row.get('Title', 'Unknown'),
        'PhotoArticleAuthor': row.get('Author', 'Unknown'),
        'PhotoJournalVolume': row.get('Volume', 'Unknown'),
        'PhotoJournalIssue': row.get('Issue', 'Unknown'),
        'PhotoJournalYear': row.get('Year', 'Unknown'),    
        'PhotoJournalInclusivePages': row.get('Pages', 'Unknown'),
        'DOI': row.get('DOI', 'Unknown')
    },
    'book': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'LoanTitle': row.get('Title', 'Unknown'),
        'LoanAuthor': row.get('Author', 'Unknown'),
        'LoanDate': row.get('Date', 'Unknown'),
    }
}