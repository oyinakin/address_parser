# Set configuration variables

ACCESS_KEY = ''
SECRET_KEY = ''
S3_BUCKET_INPUT = 'addparserlibrary'
S3_BUCKET_OUTPUT = 'output-csv-bucket'
S3_BUCKET_ARCHIVE = 'archived-input-files'
PYTESSERACT_FOLDER = r'/usr/bin/tesseract'
IMAGE_FORMAT = 'jpeg'
IMAGE_EXTENSION = '.jpeg'
TEXT_EXTENSION = '.txt'
PDF_EXTENSION = '.pdf'
CSV_EXTENSION = '.csv'
IMAGE_FILE_PREFIX = 'pdf_to_image_folder/page_'
IMAGE_FILE_FOLDER = 'pdf_to_image_folder'
OVERLAPPING_FILE_PREFIX = 'Overlapping_Entries_'
TAX_FILE_PREFIX = 'Tax_Entries_'
ENCODING_1 = 'utf-8'
ENCODING_2 = 'utf-8'
OUTPUT_FOLDER = 'output_folder_2'
INPUT_FILE_FOLDER = 'file_lists_3' 
DEFAULT_COUNTRY = 'USA'
FILTER_1 = ["ADDRESS REDACTED", "Label Matrix for local noticing", 
            "End of Label Matrix"]
START_POINT_KEYWORDS = ["Proposed Attorneys for Debtors","the debtor in this case", "CREDITOR MATRIX", 
        "Chief Restructuring Officer", "unsecured claim"]
STOP_POINT_KEYWORDS = ["CORPORATE OWNERSHIP STATEMENT", "CERTIFICATE OF MEMBERSHIP"]   
DEBTOR_NAME_FILTER = ["CREDITOR LIST, ", "CREDITOR LIST ", "CL ", "CREDITORS LIST ", "_List",
    "_CreditorsList", "- List of Creditors", "Creditors List", "_CreditorList"]
TAX_LAW_KEYWORDS = ["TAX", "LLP", "L.L.P", "ATTORNEY", " PA",
                    " ESQ", "P.C.", " PC",
                    "PC. ", "LAW OFFICE", "PREFERRED", "US BUSINESS ADMIN",
                    "SBA", "TREASURER", " SEC", "SECURITIES & EXCHANGE COMMISSION", 
                    "UNITED STATES TRUSTEE", "U.S. TRUSTEE", "US TRUSTEE", "TREASURY",
                    "UNITED STATES TREASURY", " EDD", "EMPLOYMENT DEVELOPMENT DEPARTMENT",
                    " LAW ", "STATE BOARD OF EQUALIZATION", "BANKRUPTCY COURT", 
                    "DEPARTMENT OF REVENUE", "WORKFORCE COMMISSION", "WORKFORCE DEPARTMENT",
                    "SMALL BUSINESS ADMINSTRATION", "EMPLOYMENT DEVELOPMENT DEPT", " IRS",
                    "INTERNAL REVENUE"]
