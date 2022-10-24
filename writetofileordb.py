import csv
import os
import traceback
import conf
import logging
import argparse
import boto3
from addressparser import AddressParser

logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.DEBUG)

def create_csv_file(file_name):
    s3 = boto3.resource('s3')

    # create files to save parsed adress
    main_output_file = open(conf.OUTPUT_FOLDER + '/' + file_name + \
        conf.CSV_EXTENSION, 'w', encoding=conf.ENCODING_1)
    write_to_main_output_file = csv.writer(main_output_file)
    write_to_main_output_file.writerow(["CASE NUMBER","DEBTOR","NAME","ATTENTION(OPTIONAL)","ADDRESS 1", "ADDRESS 2", \
        "CITY","STATE","POSTAL ZIP(REQUIRED)","COUNTRY(REQUIRED)","FLAGGED"])
    
    tax_file = open(conf.OUTPUT_FOLDER + '/' + conf.TAX_FILE_PREFIX + file_name + conf.CSV_EXTENSION, \
        'w', encoding=conf.ENCODING_1)
    write_to_tax_file = csv.writer(tax_file)
    write_to_tax_file.writerow(["CASE NUMBER","DEBTOR","NAME","ATTENTION(OPTIONAL)","ADDRESS 1", "ADDRESS 2", \
        "CITY","STATE","POSTAL ZIP(REQUIRED)","COUNTRY(REQUIRED)","FLAGGED"])
        
    return  (main_output_file, write_to_main_output_file, tax_file, write_to_tax_file)
    
def save_to_file(write_to_main_output_file, write_to_tax_file, details):
    try:
        if any(keyword in details[2] for keyword in conf.TAX_LAW_KEYWORDS):
            write_to_tax_file.writerow(details)
        else:              
            write_to_main_output_file.writerow(details)
    except IndexError:
        logging.error(logging.error(traceback.format_exc()))
        pass
    except TypeError:
        logging.error(logging.error(traceback.format_exc()))
        pass

def save_to_s3_bucket(file_name):
    print(555)
    s3 = boto3.resource('s3', aws_access_key_id = conf.ACCESS_KEY, 
                              aws_secret_access_key= conf.SECRET_KEY)
    filename = file_name + conf.CSV_EXTENSION   
    taxfile =  conf.TAX_FILE_PREFIX + file_name + conf.CSV_EXTENSION                      
    s3.meta.client.upload_file(conf.OUTPUT_FOLDER + '/' + filename, conf.S3_BUCKET_OUTPUT, filename)
    s3.meta.client.upload_file(conf.OUTPUT_FOLDER + '/' + taxfile, conf.S3_BUCKET_OUTPUT, taxfile)
    print(45)
        
def close_file(main_output_file,tax_file):
    main_output_file.close()
    tax_file.close()
