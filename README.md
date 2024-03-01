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
Use `-t` to run the script in test mode. This will output a list of transactions and errors to review before submitting.

Valid pickup locations include: 'Hill', 'Hunt', 'Design', 'Natural Resources', 'Veterinary Medicine', 'Textiles', 'METRC', 'Distance/Extension'.

## Data files
Place any files you want to process in the 'data_files' folder. (This folder also contains some templates and test files.) 

The file you use with this script must be a plaintext .csv file. It can include a combination of book and article request data. Each row must contain the required fields as defined by the value in the 'type' field.

\* required field

### Book request fields
* Type='book'* 
* Book title*
* Author*
* Publication date*
* Publisher
* ISSN/ISBN

### Journal request fields
* Type='article'*
* Article title*
* Journal title*
* Author*
* Year*
* Volume
* Issue
* Pages
* DOI
* ISSN/ISBN
