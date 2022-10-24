import pytesseract
import cv2
import json
import traceback
import glob
import imutils
import re
import os
import logging
import numpy as np
import pandas as pd
import conf
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from postal.parser import parse_address
from postal.expand import expand_address
from pytesseract import Output
from imutils.perspective import four_point_transform
from collections import namedtuple
from pdf2image import convert_from_path
 
pytesseract.pytesseract.tesseract_cmd = conf.PYTESSERACT_FOLDER
logging.basicConfig(format='[%(levelname)s]:%(message)s', level=logging.DEBUG)

np.random.seed(42)

class AddressParser:
    def convert_json(self, address):
        new_address = {k: v for (v, k) in address}
        json_address = json.dumps(new_address, sort_keys=True,ensure_ascii = False, indent=1)
        return new_address

    def get_file_list(self,folder_name):
        file_list =[]
        for filename in os.listdir(folder_name):
            f = os.path.join(folder_name, filename)
            # checking if it is a file
            if os.path.isfile(f):
                file_list.append(f)
        return file_list
     
    def convert_pdf_to_image(self, pdf_file):
        inputpdf = PdfFileReader(open(pdf_file, "rb"))
        no_of_Pages = inputpdf.numPages

        pdf_file_name = os.path.splitext(os.path.basename(pdf_file))[0]
        logging.info('Converting to Image...')

        start = 1
        stop = 1
        casenumber = "not traceble"
        os.makedirs(conf.IMAGE_FILE_FOLDER, exist_ok=True)
        logging.info("Iterating through all the pages")
        page_counter = 1 
        for page in range(0, no_of_Pages, 100):
            pages_chunks = convert_from_path(pdf_file, dpi=400, first_page=page,
                last_page=min(page + 100 - 1, no_of_Pages), fmt= conf.IMAGE_FORMAT
                )

            # Iterate through all the pages stored above to find the starting point
            # and stopping point of the creditor's list.
                    
            for i in range(0,len(pages_chunks)):
                filename = conf.IMAGE_FILE_PREFIX + str(page_counter) + conf.IMAGE_EXTENSION
        
                # Save the image of the page in system 
                pages_chunks[i].save(filename, conf.IMAGE_FORMAT) 
                options = "--psm 6 --oem 3"
                logging.info("Saving Page: " + str(page_counter) + " of " + str(no_of_Pages)) 
            
                # Apply image processing and convert each page to text(using tesseract)
                # and use keywords to determine start and end point for the list of addresses
                orig = cv2.imread(filename)
                image = orig.copy()
                image = imutils.resize(image, width=1500)
                current_page = pytesseract.image_to_string(cv2.cvtColor(image, cv2.COLOR_BGR2RGB),config=options)
               
                # Search for case number using regular expression
                m = re.search(r'[0-9]?(:)?(-)?(21)(-){1}([a-z,A-Z])*(-)*[0-9]{5}(-)?([a-z,A-Z])*(\()?([a-z,A-Z])*(\))?',current_page)
                if m:
                    casenumber = m.group(0).replace("Doc","")
                
                if any(keyword in current_page for keyword in conf.START_POINT_KEYWORDS): 
                    start = page_counter + 1
                    page_counter = page_counter + 1
                    continue
                if any(keyword in current_page for keyword in conf.STOP_POINT_KEYWORDS) :
                    stop = page_counter
                    page_counter = page_counter + 1
                    break
                page_counter = page_counter + 1
            else:
              continue
            break
        stop_point = stop if stop > 1 else no_of_Pages + 1
        print(casenumber)   
        return(start, stop_point, casenumber)
    
    def preprocess_page(self,image_file):
        # Apply image processing techniques to page to enhance quality
        orig = cv2.imread(image_file)
        image = orig.copy()
        image = imutils.resize(image, width=1500)
        
        ratio = orig.shape[1] / float(image.shape[1])
        # convert the image to grayscale, blur it slightly, and then apply
        # edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 3))
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
     
        # compute the Scharr gradient of the blackhat image and scale the
        # result into the range [0, 255]
        grad = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        grad = np.absolute(grad)
        (minVal, maxVal) = (np.min(grad), np.max(grad))
        grad = (grad - minVal) / (maxVal - minVal)
        grad = (grad * 255).astype("uint8")
        # apply a closing operation using the rectangular kernel to close
        # gaps in between characters, apply Otsu's thresholding method, and
        # finally a dilation operation to enlarge foreground regions
        grad = cv2.morphologyEx(grad, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        thresh = cv2.dilate(thresh, None, iterations=15)
        
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        locs=[]
        for  c in cnts:
            tableCnt = c
            (x, y, w, h) = cv2.boundingRect(tableCnt)
            locs.append((x, y, w, h))
          
        locs = sorted(locs, key=lambda x:(x[1],x[0]), reverse= False)
        entries_array = []
        bounding_box = []
        for (x, y, w, h) in locs:
                group = image[y:y + h, x:x + w]
                group = cv2.cvtColor(group, cv2.COLOR_BGR2GRAY)
                filtered = cv2.adaptiveThreshold(group.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                kernel = np.ones((1, 1), np.uint8)
                opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
                closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
                group = cv2.bitwise_or(group, closing)
                group = cv2.threshold(group, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                entries_array.append(group)
                bounding_box.append((x, y, w, h))
        return (entries_array, bounding_box ) 
        
    def extract_text(self,group):
        options = "--psm 6 --oem 3"
        text = pytesseract.image_to_string(cv2.cvtColor(group, cv2.COLOR_BGR2RGB), config=options)
        return text 

    def remove_unwanted_text_or_character(self,text):
        # Process text generated from tesseract

        # Split text to form an array rather than a multi-lined string
        split_into_csv_format = text.split("\n")
        
        # Remove unwanted characters and empty spaces.
        try:
            split_into_csv_format.remove('\x0c')
            split_into_csv_format.remove('')
        except IndexError:
            pass
        except ValueError:
            pass
          
        #Remove unwanted text that do not represent address and return
        if len(split_into_csv_format) <= 1:
            return []
        elif "Filed" in text or "Entered" in text or "Page" in text \
                or re.search(r'\b[p|P]+(age)*\s*[0-9]+\s+\b[o|O]*(f)+\s+[0-9]+',text) \
                or re.search(r'(\d{7})(.)(\d)',text):
            return []
        else:   
            # Check for addresses with 'ADDRESS REDACTED' and ignore otherwise
            # assign address to a variable of type array and return array
            if any(keyword in text for keyword in conf.FILTER_1):
                return
            elif len(split_into_csv_format) > 2:
                cleaned_text = []
                cleaned_text = split_into_csv_format
                return cleaned_text
                
    def clean_up_line_in_text_file(self, each_line, case_number):
        cleaned_text = each_line.split("|")
        if cleaned_text:
            for line in cleaned_text:
                if line == "" or case_number in line :
                    try:
                        cleaned_text.remove(line) 
                    except ValueError:
                        pass
                line = line.strip()  
        return cleaned_text 
        
    def process_text(self, cleaned_text, debtor, case_number):
        # Define and intialise variables for each parsed address field
        name = ""
        attention = ""
        address1 = ""
        address2=""
        city =""
        state =""
        postal=""
        country =""
        flagged = ""
        details=[]
        incareof = ""
        
        if cleaned_text is None:
            return []
        else:
            # Parse lines with ATTENTION and C/O(in care of) as libportal is not able to parse these correctly.
            # Remove the lines once parsed
            for each_line in cleaned_text:
                if any(keyword in each_line.upper() for keyword in ["CIO", "C/O" , "C/Q","CiO"]):
                    incareof = each_line
                    cleaned_text.remove(each_line)
                    
                if any(keyword in each_line.upper() for keyword in ["ATTN", "ATTN:" , "ATIN", "ATTENTION"]):
                    attention = each_line
                    try: 
                        cleaned_text.remove(each_line)
                    except ValueError:
                        pass

            # Apply libportal to cleaned address                        
            parsed_address = parse_address(" ".join(cleaned_text))
            json_address = self.convert_json(parsed_address)
            key_list = list(json_address.keys())
            
            if "house_number" in key_list:
                address1  = json_address.get("house_number").upper()
            if "road" in key_list:
                address1  = address1 + ' ' + json_address.get("road").upper()
            if "level" in key_list:
                address2  =address2 + ' ' + json_address.get("level").upper()
            if "unit" in key_list:
                address2  = address2 + ' ' + json_address.get("unit").upper()
            if "city" in key_list:
                city  = json_address.get("city").upper()
            if "city_district" in key_list:
                address2  = address2 + ' ' + json_address.get("city_district")
            if "state" in key_list:
                state  = json_address.get("state").upper()
            if "country" in key_list:
                country  = country + ' ' + json_address.get("country").upper()
            if "po_box" in key_list:
                address1  = json_address.get("po_box").upper()
            if "postcode" in key_list:
                postal  =  json_address.get("postcode").upper()
            if "suburb" in key_list:
                address2  = address2 + ' ' + json_address.get("suburb").upper()
            if "house" in key_list:
                name  = json_address.get("house").upper()
            else:
                nn  = self.convert_json(parse_address(cleaned_text[0].strip().upper()))
                if "house_number" in list(nn.keys()) or "city" in list(nn.keys()) \
                    or "po_box" in list(nn.keys()) or "postcode" in list(nn.keys()) :
                    flagged = "FLAGGED"
                    name = ""
                    
                else:
                    name = cleaned_text[0].strip().upper()  
            if 'DUPLICATE' in name.upper(): 
                name  = cleaned_text[0].strip().upper()    
            if incareof != "":
                name = name + "\n" + incareof.upper()
            name =name.replace("*", "")
            if country == "":
                country = conf.DEFAULT_COUNTRY    
        details = [case_number,debtor,name,attention,address1, address2,city,state,postal, country, flagged]   
        return details
   
     
    


