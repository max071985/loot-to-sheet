from spreadsheetManager import SpreadsheetManager
from templateProcessing import ImageProcessingManager

def main():
    imageProc_Manager = ImageProcessingManager()
    spreadsheet_Manager = SpreadsheetManager()

    imageProc_Manager.processImage()


if __name__ == "__main__":
    main()
