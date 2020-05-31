import json
from datetime import datetime, timedelta
import bns

import utilities
from google.cloud import storage
import google.auth
import os

currencies = ["USD","CAD","EUR","GBP"]
storage_client = storage.Client()
bucket = storage_client.bucket('{bucket_details}')

def get_daily_rates():
    ''' Reading the configuration file for calls to get Cambio FX Rates
    '''
    blob = bucket.blob('config/dealers.json')
    downloaded_blob = blob.download_as_string()

    data = json.loads(downloaded_blob.decode("utf-8"))

    for i in range(len(data)):
        if (data[i].get('enabled')):
            #print(data[i].get('code'))
            if (data[i].get('code') == 'ABC'):
                # Call Scraped and send to custom bank parsing
                #print(data[i].get('code'))
                bns.get_fx_rates(data[i].get('code'),data[i].get('url'),str(datetime.date(datetime.now())),data[i].get('currencies'))
            elif (data[i].get('code') == 'XYC'):
                # Call Scraped and send to custom bank parsing
                #print(data[i].get('code'))
                ncb.get_fx_rates(data[i].get('code'),data[i].get('url'),str(datetime.date(datetime.now())),data[i].get('currencies'))

    #print(datetime.date(datetime.now()))
    r = utilities.get_rates(str(datetime.date(datetime.now())),currencies)
    utilities.generate_csv(str(datetime.date(datetime.now())))
    # Cleanup previous day data
    d = datetime.today() - timedelta(days=1)
    utilities.clear_data(str(datetime.date(d)))
    #utilities.send_data(emails)

    return

def get_sheet():
    ''' Reading the configuration file for calls to get Cambio FX Rates
    '''
    d = str(datetime.date(datetime.now()))
    #print(d)
    #print('output/'+d+'.xlsx')
    # Get Presigned URL details from Google Cloud Storage
    blob = bucket.blob('output/'+d+'.xlsx')
    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )

    return url
