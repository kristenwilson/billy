# Bulk ILL Prototype
## Description
A Python script that creates Interlibrary Loan (ILL) transactions from a file of citation data.
## Prerequisites
You must have Python3 installed.
## Usage
`python3 bulk_ill_alpha.py email filename`

`email` must be a valid email address associated with an active ILLiad account.

`filename` must be the name of a file saved to the `data_files` folder.

### Upload file
The file you use with this script must be a plaintext .csv file that includes the following columns:
* Title
* Journal title
* Author
* Volume
* Issue
* Year
* Pages
* DOI

### ILLiad API
To connect to the ILLiad API, ask your ILLiad administrator to create an API key for this project. You will also need the base URL for your ILLiad system. It will look like `https://your.illiad.edu/ILLiadWebPlatform`.

### Config
Use `config.py.template` to create `config.py`. Fill in the values for your ILLiad API base URL and key.
