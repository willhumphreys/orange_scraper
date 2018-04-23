# Orange Scraper

An AWS Lambda to scrape sentiment data and pull matching price data Using REST from https://1forge.com/forex-data-api
 
The lambda needs the following information

```json
{
  "forge_api_key": "api_key",
  "data_url": "site_to_scrape",
  "db_table": "dynamo_db_table"
}
``` 

## Dependencies that need to be installed

```
python3.6 -m pip install BeautifulSoup4 -t .
python3.6 -m pip install requests -t .
python3.6 -m pip install boto3 -t .
```

## Alias for pipenv
```
alias prp="pipenv run python"
```

## How to install a dependency
```
pipenv install BeautifulSoup4
```

## Run the tests
```
py.test
```
