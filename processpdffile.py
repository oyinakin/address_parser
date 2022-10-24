import csv
import os
import traceback
import conf
import logging
import argparse
import writetofileordb as wfd
from addressparser import AddressParser


def process_pdf_file(pdf_file):
    
    ap = AddressParser()
    file_name = os.path.splitext(os.path.basename(pdf_file))[0]
    debtor = file_name
    for filter in conf.DEBTOR_NAME_FILTER:
        debtor = debtor.replace(filter, "")
    
    # Create text file to save overlapping entries.
    text_file = open(conf.OUTPUT_FOLDER + '/' + conf.OVERLAPPING_FILE_PREFIX + file_name, 'w')
    
    # Create all neccessary output files
    (main_output_file, write_to_main_output_file, tax_file, \
        write_to_tax_file) = wfd.create_csv_file(file_name)
            
    # Convert each pdf page to an image
    (start, stop, case_number) = ap.convert_pdf_to_image(pdf_file)
    
    # Process each page now stored as image
    for i in range(start, stop):
        page =  conf.IMAGE_FILE_PREFIX + str(i) + conf.IMAGE_EXTENSION
        (all_entries_on_page, bounding_box) = ap.preprocess_page(page)
        
        for (j,each_entry) in enumerate(all_entries_on_page):
            text = ap.extract_text(each_entry)
            cleaned_text = ap.remove_unwanted_text_or_character(text)
            
            # Check for overlapping address based on width of text.
            # If overlapping occurs, save in a different file and skip current loop.
            if cleaned_text and len(cleaned_text) > 2 :
                cleaned_text_width = bounding_box[j][3]
                if cleaned_text_width > 750:
                    text_file.write(('\n').join(cleaned_text) + "\n\n\n" )
                    continue
              
                # Parse cleaned text into columns and save in .csv files   
                details = ap.process_text(cleaned_text, debtor, case_number)
                if len(details) > 0:
                    wfd.save_to_file(write_to_main_output_file, write_to_tax_file, details)
            
    text_file.close()
    wfd.close_file(main_output_file,tax_file)
    wfd.save_to_s3_bucket(file_name)
    # remove converted pages once extraction is complete          
    for filename in os.listdir(conf.IMAGE_FILE_FOLDER):
        os.remove(conf.IMAGE_FILE_FOLDER + '/' + filename)