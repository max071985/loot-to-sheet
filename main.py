from spreadsheetManager import SpreadsheetManager
from templateProcessing import ImageProcessingManager
import templateProcessing
from fileManager import FileManager
import tkinter as tk
import tkinter.filedialog as fd
from PIL import Image, ImageTk

UI_IMAGE_SIZE = (300, 150)
IMAGE_PADDING = 5

SPREADSHEET_ID = "1Sm6mlw-HxIqW3fZdIcm9mxJwAnCcxZjMXHNjm2JxPWI"
root = tk.Tk()
root.geometry("1024x576")

#TODO: Reorganize this whole file into a designated UI class.
#Init global vars
image_list = []
btnOpenFiles, btnDeleteImages, loadedFiles = None, None, None

#Init global agents
image_processing_agent = ImageProcessingManager()
# spreadsheet_agent = SpreadsheetManager(SPREADSHEET_ID)

def main():
    global image_processing_agent
    FileManager.clear_folder(templateProcessing.INPUT_PATH)
    init_UI()
    
def init_UI():
    global btnOpenFiles, btnDeleteImages, loadedFiles
    btnOpenFiles = tk.Button(root, text="Import images", command=load_Images)
    btnOpenFiles.grid(column=0, row=0)
    
    loadedFiles = tk.Text(root)
    loadedFiles.config(state=tk.DISABLED)
    loadedFiles.grid(column=0, row= 1)

    btnDeleteImages = tk.Button(root, text="Delete images", command=delete_Images)
    btnDeleteImages.grid(column=0, row = 2)
    root.mainloop()

def load_Images():
    global loadedFiles, image_list, image_processing_agent
    files = fd.askopenfilenames(parent=root, title='Choose image files')
    for f in files:
        try:
            temp = Image.open(f)
            temp.thumbnail(UI_IMAGE_SIZE, Image.ANTIALIAS)
            new_image = ImageTk.PhotoImage(temp)
            image_list.append(new_image)
            loadedFiles.image_create(tk.END, image=new_image, padx=IMAGE_PADDING)
        except Exception as e:
            print(e)
        else:
            #TODO: Add image processing queue for a case where there are more than 1 image imputted.
            pass

def delete_Images():
    global loadedFiles, image_list
    image_list.clear()
    loadedFiles.delete('1.0', tk.END)

if __name__ == "__main__":
    main()
