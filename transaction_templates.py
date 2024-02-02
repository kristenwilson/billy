def get_transaction_templates(email, pickup):
    return {
     'article': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': 'Unknown',
        'PhotoArticleTitle': 'Unknown',
        'PhotoArticleAuthor': 'Unknown',
        'PhotoJournalVolume': 'Unknown',
        'PhotoJournalIssue': 'Unknown',
        'PhotoJournalYear': 'Unknown',    
        'PhotoJournalInclusivePages': 'Unknown',
        'DOI': 'Unknown',
    },
    'book': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'LoanTitle': 'Unknown',
        'LoanAuthor': 'Unknown',
        'LoanDate': 'Unknown',
    }
}