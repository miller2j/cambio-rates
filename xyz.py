import bs4 as bs
import requests
import time
import os
import json
#import requests.exceptions.HTTPError as HTTPError
from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket('{bucket_details}')

session = requests.Session()
header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36","X-Requested-With": "XMLHttpRequest"}

def get_fx_rates(code,url,current_date,currencies):
    ''' Get list of FX Rates from XYZ Cambio, by parsing scraped content.
    Parameters:
            code: code for the entity.
            url: path to content retrieval.
            current_date: string of current data, e.g. '2020-03-25'
            currencies: array list of currencies to be retrieved
    Processing:
            Writes currency values to respective date currency file, e.g. '2020-03-25_XYZ.json'

    Returns:
            -
    '''
    req = session.get(url, headers = header, allow_redirects=True)
    html = req.content
    soup = bs.BeautifulSoup(html,'html.parser')
    # Select tag, class or HTML attribute to identify the table to retrieve rates
    table = soup.select_one('.xyz--table').tbody
    ttmp = []
    itertable = iter(table)
    next(itertable)
    next(itertable)
    for row in itertable:
        tmp = {}
        tmp['currency'] = row.contents[0].contents[0]
        tmp['cash'] = {"buy": row.contents[2].contents[0], "sell": row.contents[6].contents[0]}
        tmp['cheque'] = {"buy": row.contents[4].contents[0], "sell": row.contents[6].contents[0]}
        ttmp.append(tmp)
    # Place details in Google Cloud Storage
    blob = bucket.blob('data/'+current_date+'_'+code+'.json')
    blob.upload_from_string(json.dumps(ttmp))

    return
