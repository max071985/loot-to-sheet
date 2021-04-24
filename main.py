from spreadsheetManager import SpreadsheetManager
from templateProcessing import ImageProcessingManager

SPREADSHEET_ID = "1Sm6mlw-HxIqW3fZdIcm9mxJwAnCcxZjMXHNjm2JxPWI"

def main():
    imageProc_Manager = ImageProcessingManager()
    #spreadsheet_Manager = SpreadsheetManager(SPREADSHEET_ID)

    imageProc_Manager.processImage()
    
    


if __name__ == "__main__":
    main()
