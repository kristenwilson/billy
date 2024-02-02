# Bulk ILL Script
## Description
A Python script that creates interlibrary loan (ILL) transactions from a file of citation data.

## Prerequisites
### ILLiad API
To connect to the ILLiad API, ask your ILLiad administrator to create an API key for this project. You will also need the base URL for your ILLiad system. It will look like `https://your.illiad.edu/ILLiadWebPlatform`.
### Config
Use `config.py.template` to create `config.py`. Fill in the values for your ILLiad API base URL and key.

## Usage
```python
python3 bulk_ill.py you@university.edu file.csv -p 'Pickup Location'
```

## Upload file
The file you use with this script must be a plaintext .csv file 

Required fields
* Type (supported values are "book" or "article")

Book request fields
* Title
* Author
* Date

Journal request fields
* Article title
* Journal title
* Author
* Volume
* Issue
* Year
* Pages
* DOI


