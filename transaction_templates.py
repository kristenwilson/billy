def get_transaction_templates(email, pickup):
    return {
     'article': {
        'ExternalUserId': email,
        'RequestType': 'Article',
        'ProcessType': 'Borrowing',
        'PhotoJournalTitle': 'Journal title',
        'PhotoArticleTitle': 'Title',
        'PhotoArticleAuthor': 'Author',
        'PhotoJournalVolume': 'Volume',
        'PhotoJournalIssue': 'Issue',
        'PhotoJournalYear': 'Year',    
        'PhotoJournalInclusivePages': 'Pages',
        'DOI': 'DOI',
    },
    'book': {
        'ExternalUserId': email,
        'ItemInfo4': pickup,
        'RequestType': 'Loan',
        'ProcessType': 'Borrowing',
        'LoanTitle': 'Title',
        'LoanAuthor': 'Author',
        'LoanDate': 'Date',
    }
}