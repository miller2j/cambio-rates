import glob
import os
import json
from functools import reduce
import xlsxwriter
from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket('{bucket_details}')

def get_rates(current_date,currencies):
    ''' Get min and max rates for list of currencies
    '''
    values = []
    all_data = []
    all_code = []
    all_brokers = []
    # Get details in Google Cloud Storage
    blobs = storage_client.list_blobs(
        '{bucket_details}', prefix='data/'+current_date+'_'
    )
    for blob in blobs:
        #print(blob.name)
        b = json.loads(bucket.blob(blob.name).download_as_string().decode("utf-8"))
        all_brokers.append({'code': blob.name.split('_')[1].split('.')[0]})
        all_code.append({'code': blob.name.split('_')[1].split('.')[0], 'values':b})
        #all_data.append(data)
        all_data.extend(b)
    #end of for loop
    currency = []
    for c in currencies:
        t = list(filter(lambda x : x['currency'] == c, all_data))
        #print(t)
        l = list(map(lambda x: x.get('cash', {'buy':'-','sell':'-'}).get('buy', "-"), t))
        while("-" in l) :
            l.remove("-")
        ll =  list(map(lambda x: x.get('cash', {'buy':'-','sell':'-'}).get('sell', "-"), t))
        while("-" in ll) :
            ll.remove("-")
        lll = list(map(lambda x: x.get('cheque', {'buy':'-','sell':'-'}).get('buy', "-"), t))
        while("-" in lll) :
            lll.remove("-")
        llll = list(map(lambda x: x.get('cheque', {'buy':'-','sell':'-'}).get('sell', "-"), t))
        while("-" in llll) :
            llll.remove("-")
        #print(l)
        currency.append({'name': c,
                        'cash': {'buy': {'min': min(l), 'max': max(l)}, 'sell': {'min': min(ll), 'max': max(ll)}},
                        'cheque':{'buy':{'min': min(lll), 'max': max(lll)}, 'sell':{'min': min(llll), 'max': max(llll)}}})
        #print('------')
    # Place details in Google Cloud Storage
    bl = bucket.blob('output/'+current_date+'.json')
    bl.upload_from_string(json.dumps(all_data))
    bl = bucket.blob('output/'+current_date+'_currencies.json')
    bl.upload_from_string(json.dumps(currency))
    bl = bucket.blob('output/'+current_date+'_brokers.json')
    bl.upload_from_string(json.dumps(all_brokers))
    bl = bucket.blob('output/'+current_date+'_code.json')
    bl.upload_from_string(json.dumps(all_code))

    return

def generate_csv(current_date):
    ''' Generate CSV for date supplied
    '''
    # Create a workbook and add a worksheet.
    #workbook = xlsxwriter.Workbook('output/'+current_date+'.xlsx')
    workbook = xlsxwriter.Workbook('/tmp/'+current_date+'.xlsx')
    worksheet = workbook.add_worksheet()
    d = []
    c = []
    b = []
    a = []
    # Open file from Google Cloud Storage
    d = json.loads(bucket.blob('output/'+current_date+'.json').download_as_string().decode("utf-8"))
    b = json.loads(bucket.blob('output/'+current_date+'_brokers.json').download_as_string().decode("utf-8"))
    c = json.loads(bucket.blob('output/'+current_date+'_currencies.json').download_as_string().decode("utf-8"))
    a = json.loads(bucket.blob('output/'+current_date+'_code.json').download_as_string().decode("utf-8"))

    bold = workbook.add_format({'bold': True})
    center = workbook.add_format({'bold': True, 'align': 'center'})
    # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0
    worksheet.write(row, col, 'Date: '+current_date, bold)
    row += 1
    ref_row_1 = row
    worksheet.write(row, col, 'Institutions', bold)
    row += 1
    ref_row_2 = row
    # Iterate over the data and write brokers
    for item in (b):
        worksheet.write(row, col, item['code'], bold)
        row += 1

    # Iterate over the data and write currencies
    col = 1
    row = 0
    d_rows = ref_row_2
    red = workbook.add_format({'color': 'red', 'align': 'center'})
    green = workbook.add_format({'color': 'green', 'align': 'center'})
    for item in (c):
        ref_row_2 = d_rows
        worksheet.merge_range(row, col, row, (col+1), item['name'], center)
        worksheet.write((row+1), col, 'Buy Cash')
        worksheet.write((row+1), (col+1), 'Sell Cash')
        for it in (a):
            worksheet.write(ref_row_2, 0, it['code'])
            for i in (it['values']):

                if (i['currency']==item['name']) :
                    worksheet.write(ref_row_2, col, i['cash']['buy'])
                    worksheet.write(ref_row_2, (col+1), i['cash']['sell'])
            ref_row_2 +=1
        worksheet.write(ref_row_2, col, 'Max')
        worksheet.write(ref_row_2, (col+1), 'Min')
        worksheet.write((ref_row_2+1), col, item['cash']['buy']['max'])
        worksheet.write((ref_row_2+1), (col+1), item['cash']['sell']['min'])
        # Applying multiple styles
        if (float(item['cash']['buy']['max']) > float(item['cash']['sell']['min'])):
            worksheet.merge_range((ref_row_2+2), col, (ref_row_2+2), (col+1), "")
            worksheet.write_formula((ref_row_2+2), col, '=_xlfn.VAR.S('+item['cash']['buy']['max'].strip()+','+item['cash']['sell']['min'].strip()+')', green)
        else:
            worksheet.merge_range((ref_row_2+2), col, (ref_row_2+2), (col+1), "")
            worksheet.write_formula((ref_row_2+2), col, '=_xlfn.VAR.S('+item['cash']['buy']['max'].strip()+','+item['cash']['sell']['min'].strip()+')', red)
            # =VAR.S(buy_max, buy_min)

        col += 2
    # Close workbook
    workbook.close()
    bucket.blob('output/'+current_date+'.xlsx').upload_from_filename('/tmp/'+current_date+'.xlsx')
    # Remove tmp file
    os.remove('/tmp/'+current_date+'.xlsx')
    return

def clear_data(remove_date):
    ''' Remove files with supplied date
    '''
    # Get details in Google Cloud Storage
    blobs = storage_client.list_blobs(
        '{bucket_details}', prefix='data/'+remove_date+'_'
    )
    for blob in blobs:
        print(blob.name)
        bucket.blob(blob_name).delete()
    # Get details in Google Cloud Storage
    blobs = storage_client.list_blobs(
        '{bucket_details}', prefix='output/'+remove_date
    )
    for blob in blobs:
        print(blob.name)
        bucket.blob(blob_name).delete()


    return
