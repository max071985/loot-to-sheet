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
btnOpenFiles, btnDeleteImages, btnProcess ,loadedFiles, lblOutput = None, None, None, None, None

#Init global agents
image_processing_agent = ImageProcessingManager()
spreadsheet_agent = SpreadsheetManager(SPREADSHEET_ID)
# spreadsheet_agent = SpreadsheetManager(SPREADSHEET_ID)

class InputImage():
    def __init__(self, image_path):
        self.image_path = image_path
        temp = Image.open(image_path) #Get object
        temp.thumbnail(UI_IMAGE_SIZE, Image.ANTIALIAS) #Resize
        self.image_Obj = ImageTk.PhotoImage(temp)


def main():
    global image_processing_agent
    FileManager.clear_folder(templateProcessing.INPUT_PATH)
    init_UI()
    
def init_UI():
    global btnOpenFiles, btnDeleteImages, loadedFiles, btnProcess, lblOutput
    btnOpenFiles = tk.Button(root, text="Import images", command=load_Images)
    btnOpenFiles.grid(column=0, row=0)
    
    loadedFiles = tk.Text(root)
    loadedFiles.config(state=tk.DISABLED)
    loadedFiles.grid(column=0, row= 1)

    btnDeleteImages = tk.Button(root, text="Delete images", command=delete_Images)
    btnDeleteImages.grid(column=0, row = 2)

    btnProcess = tk.Button(root, text="Process images", command=process_Images)
    btnProcess.grid(column=1, row=2)

    lblOutput = tk.Label(root)
    lblOutput.grid(column = 0, row = 3)
    root.mainloop()

def load_Images():
    global loadedFiles, image_list, image_processing_agent
    files = fd.askopenfilenames(parent=root, title='Choose image files')
    for f in files:
        try:
            new_image = InputImage(f)
            image_list.append(new_image)
            loadedFiles.image_create(tk.END, image=new_image.image_Obj, padx=IMAGE_PADDING)
        except Exception as e:
            print(e)
        else:
            #TODO: Add image processing queue for a case where there are more than 1 image imputted.
            pass

def delete_Images():
    global loadedFiles, image_list
    image_list.clear()
    loadedFiles.delete('1.0', tk.END)

def process_Images():
    global image_processing_agent, image_list, lblOutput
    i = 0
    for image in image_list:
        image_processing_agent.setImage(image.image_path)
        image_processing_agent.setLootTable("blood_wolf")
        print("Processing image... %d" % i)
        image_processing_agent.processImage()
        print("Done %d." % i)
    print("Finished processing all the images.\nResults:\n")
    lblOutput['text'] = image_processing_agent.getTotalMatches()
    image_processing_agent.test()

if __name__ == "__main__":
    main()
