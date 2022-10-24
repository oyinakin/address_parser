import csv
import cred
import os
import shutil
import traceback
import conf
import logging
import argparse
import processpdffile as ppf
import processtextfile as ptf
from addressparser import AddressParser


logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)

# Create an instance of the AddressParser class
ap = AddressParser()
cred.s3_access()
file_list = ap.get_file_list(conf.INPUT_FILE_FOLDER) 
try:
    # Create an output folder to store the csv and text files.
    os.makedirs(conf.OUTPUT_FOLDER, exist_ok=True)

    # Iterate through each file and parse address       
    for each_file in file_list:

        # Get file name and file extension
        file_name = os.path.splitext(os.path.basename(each_file))[0]
        file_extension = os.path.splitext(os.path.basename(each_file))[1]
        
        logging.info("Processing " + file_name + file_extension)
                
        #check if file extension is .pdf or .txt and process accordingly
        if file_extension == conf.PDF_EXTENSION:
            ppf.process_pdf_file(each_file)
        
        if file_extension == conf.TEXT_EXTENSION:
            ptf.process_text_file(each_file)
except:
    logging.error(traceback.format_exc())
	
cred.archive_input_files()	

shutil.rmtree(conf.INPUT_FILE_FOLDER, ignore_errors=True)