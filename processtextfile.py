import csv
import os
import traceback
import conf
import logging
import argparse
import writetofileordb as wfd
from addressparser import AddressParser

def process_text_file(text_file):
    ap = AddressParser()
    
    file_name = os.path.splitext(os.path.basename(text_file))[0]
    debtor = file_name
    for filter in conf.DEBTOR_NAME_FILTER:
        debtor = debtor.replace(filter, "")
    
    # Create all neccessary output files
    (main_output_file, write_to_main_output_file, tax_file, \
        write_to_tax_file) = wfd.create_csv_file(file_name)
    

    with open(text_file, 'r', encoding = conf.ENCODING_2) as tf:
        lines = [line.rstrip() for line in tf]
    
    # Extract Case Number and remove unwanted lines
    case_number= ""
    for each_line in lines:
        if "case number:" in each_line.lower():
            case_number = (each_line.split('Case Number:')[1]).strip()
            continue
        if "total labels"  in each_line.lower():
            continue
        if "undeliverable"  in each_line.lower():
            continue
        # Remove empty lines
        if each_line is "":
            lines.remove(each_line)
            continue
        cleaned_text = ap.clean_up_line_in_text_file(each_line, case_number)    
        details = ap.process_text(cleaned_text, debtor, case_number)
        if details:
            wfd.save_to_file(write_to_main_output_file, write_to_tax_file, details)
            
    wfd.close_file(main_output_file,tax_file)
    wfd.save_to_s3_bucket(file_name)             
