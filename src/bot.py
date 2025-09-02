#!/usr/bin/env python3

# imports
import http.client
import json
from urllib.parse import quote
from report import generate_report
from email_sender import send_email

# load config
with open('config.json', 'r') as f:
    config = json.load(f)

# search all pages
def search_zillow():
    # batch locations
    locations = config['search_params']['locations']
    locations = locations.split(';')
    locations_batches = [locations[i:i+5] for i in range(0, len(locations), 5)]

    # search each batch
    results = []
    for locations in locations_batches:
        # first page search
        page_number = 1
        while True:
            data = search(page_number, locations)
            results.extend(data['props'])
            if data['totalPages'] == page_number:
                break
            page_number += 1

    return results


# single page search
def search(page_number, locations):
    api_host = config['api']['host']
    api_key = config['api']['key']
    endpoint_path = config['api']['endpoint_path']
    status_type = config['search_params']['status_type']
    home_type = config['search_params']['home_type']
    sort = config['search_params']['sort']
    max_price = config['search_params']['max_price']
    days_on = config['search_params']['days_on']
    
    # create connection
    conn = http.client.HTTPSConnection(api_host)
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': api_host
    }

    # format locations string
    locations = [location.strip() for location in locations]
    locations = ";".join(locations)

    # make request
    request_url = f"{endpoint_path}?location={locations.replace(' ', '%20').replace(',', '%2C')}&status_type={status_type}&home_type={home_type}&sort={sort}&maxPrice={max_price}&daysOn={days_on}&page={page_number}"
    conn.request("GET", request_url, headers=headers)
    res = conn.getresponse()
    data = res.read()

    # parse response
    data = json.loads(data.decode("utf-8"))
    return data

# orchestrate
def main():
    # search zillow
    results = search_zillow()

    # generate report
    report = generate_report(results)

    # send email
    send_email(report, config['email_list'])
    
if __name__ == "__main__":
    main()