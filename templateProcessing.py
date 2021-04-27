from skimage.metrics import structural_similarity as ssim
from cv2 import cv2
import numpy as np
from singleton import Singleton
from pathlib import Path
import pytesseract
from fileManager import FileManager
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Constants
DEFAULT_TEMPLATE_MATCHING_THRESHOLD = 0.5 # Threshold for template matching resemblance
NMS_THRESHOLD = 0.2 # Threshold for overlapping function
OUTPUT_FILE_PATH = f"output/result.jpeg"
INPUT_PATH = f"input_image"
TEMPLATE_PATH = f"templates"

# BDO UI Measurements
USER_UI_SCALE = 1
BDO_ITEM_SQUARE_WIDTH = 45 * USER_UI_SCALE
BDO_ITEM_SQUARE_HEIGHT = 45 * USER_UI_SCALE
BDO_ITEM_SQUARE_PADDING = 4 * USER_UI_SCALE

INITIAL_X_PADDING = 4 * USER_UI_SCALE
INITIAL_Y_PADDING = 12 * USER_UI_SCALE

class Template:
    """Represents a template image
    """
    def __init__(
        self,
        image_path,
        label,
        color,
        matching_threshold=DEFAULT_TEMPLATE_MATCHING_THRESHOLD,
    ):
        self.image_path = image_path
        self.label = label
        self.color = color
        self.template = cv2.imread(image_path)
        self.template_height, self.template_width = self.template.shape[:2]
        self.matching_threshold = matching_threshold

#TODO: Add image processing queue
class ImageProcessingManager(metaclass=Singleton):
    """Handles all image related stuff

    Args:
        metaclass Singleton instance
    """
    def __init__(self, image_path="input_image/ronaros1.png", templates=None):
        self._image = cv2.imread(image_path)  # Image to process.
        if templates is None: #Default go-to template.
            self._templates = [
                Template(
                    image_path="templates/main/aa_temp.png", label="1", color=(125, 0, 255)
                ),
            ]
        self._detections = []
        self._cropped_detections = []
        self._squares = []
        self._square_img = []

    def setImage(self, image_path):
        self._image = cv2.imread(image_path)

    def compute_iou(self, boxA, boxB):
        xA = max(boxA["TOP_LEFT_X"], boxB["TOP_LEFT_X"])
        yA = max(boxA["TOP_LEFT_Y"], boxB["TOP_LEFT_Y"])
        xB = min(boxA["BOTTOM_RIGHT_X"], boxB["BOTTOM_RIGHT_X"])
        yB = min(boxA["BOTTOM_RIGHT_Y"], boxB["BOTTOM_RIGHT_Y"])
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        boxAArea = (boxA["BOTTOM_RIGHT_X"] - boxA["TOP_LEFT_X"] + 1) * (
            boxA["BOTTOM_RIGHT_Y"] - boxA["TOP_LEFT_Y"] + 1
        )
        boxBArea = (boxB["BOTTOM_RIGHT_X"] - boxB["TOP_LEFT_X"] + 1) * (
            boxB["BOTTOM_RIGHT_Y"] - boxB["TOP_LEFT_Y"] + 1
        )
        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    def non_max_suppression(
        self,
        objects,
        non_max_suppression_threshold=0.5,
        score_key="MATCH_VALUE",
    ):
        sorted_objects = sorted(objects, key=lambda obj: obj[score_key], reverse=True)
        filtered_objects = []
        for object_ in sorted_objects:
            overlap_found = False
            for filtered_object in filtered_objects:
                iou = self.compute_iou(object_, filtered_object)
                if iou > non_max_suppression_threshold:
                    overlap_found = True
                    break
            if not overlap_found:
                filtered_objects.append(object_)
        return filtered_objects

    def processImage(self):
        """Main process function. responsable to locate the initial template and calls sub-functions to locate the rest of the items.
        """
        try:
            # Go over the templates list
            for template in self._templates:
                template_matching = cv2.matchTemplate(
                    template.template, self._image, cv2.TM_CCOEFF_NORMED
                )

                match_locations = np.where(
                    template_matching >= template.matching_threshold
                )

                # Build detection information objects into _detections[]
                for (x, y) in zip(match_locations[1], match_locations[0]):
                    match = {
                        "TOP_LEFT_X": x,
                        "TOP_LEFT_Y": y,
                        "BOTTOM_RIGHT_X": x + template.template_width,
                        "BOTTOM_RIGHT_Y": y + template.template_height,
                        "MATCH_VALUE": template_matching[y, x],
                        "LABEL": template.label,
                        "COLOR": template.color,
                    }
                    self._detections.append(match)
            # Get rid of overlapping/overstacking (shouldn't exist, but might)
            self._detections = self.non_max_suppression(
                self._detections, non_max_suppression_threshold=NMS_THRESHOLD
            )
            image_with_detections = self._image.copy() # Copy of the main image to work on
            # Iterate over the found template detections in the image
            for detection in self._detections:
                # Draw a rectangle around the detection:
                self.drawSquareAroundDetection(detection, image_with_detections)
                # Create a new image from the detection and add it to _cropped_detections[] list (USED FOR DEBUGGING CURRENTLY)
                detection_img = image_with_detections[detection["TOP_LEFT_Y"]: detection["BOTTOM_RIGHT_Y"], detection["TOP_LEFT_X"]: detection["BOTTOM_RIGHT_X"]]
                self._cropped_detections.append(detection_img)
            # Create an output folder in case it doesn't exist.
            Path("output").mkdir(
                parents=True, exist_ok=True
            ) 
            # Find and process inventory items
            self.findItemSquares(image_with_detections, 15, self._detections[0]["TOP_LEFT_X"], self._detections[0]["BOTTOM_RIGHT_Y"])
            # Save a new image with all the drawn detections (DEBUGGING)
            cv2.imwrite(OUTPUT_FILE_PATH, image_with_detections) 
        except Exception as e: #TODO
            print(e)
        else:
            print(
                f"Successfully processed the image. The output is located at: {OUTPUT_FILE_PATH}"
            )

    def drawSquareAroundDetection(self, detection, image_with_detections):
        """Draw a square around the detection.

        Args:
            detection ([Template]): [stores information about a detection within the bigger picture]
        """
        cv2.rectangle(
                    image_with_detections,
                    (detection["TOP_LEFT_X"], detection["TOP_LEFT_Y"]),
                    (detection["BOTTOM_RIGHT_X"], detection["BOTTOM_RIGHT_Y"]),
                    detection["COLOR"],
                    2,
                )
        cv2.putText(
                    image_with_detections,
                    f"{detection['LABEL']} - {detection['MATCH_VALUE']}",
                    (detection["TOP_LEFT_X"] + 2, detection["TOP_LEFT_Y"] + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    detection["COLOR"],
                    1,
                    cv2.LINE_AA,
                )

    def findItemSquares(self, image_with_detections, amount, init_top_left_x, init_top_left_y):
        """Go over inventory rows for amount of times

        Args:
            image_with_detections (cv2 image): image that will have the detections
            amount (int): Number of items to iterate over
            init_top_left_x (int): X Coordinate of the Auto Arrange inventory button
            init_top_left_y (int): Y Coordinate of the Auto Arrange inventory button (LOWER level!)
        """
        x, y = init_top_left_x, init_top_left_y

        # Find the first square's top left corner (need to move down right diagonally)
        x += INITIAL_X_PADDING
        y += INITIAL_Y_PADDING

        for i in range(amount): # TODO: add exceptions to certain items.
            if i % 8 == 0 and i > 0: # Go down 1 row (reset X to start and increase Y amount to match next row)
                x = init_top_left_x + INITIAL_X_PADDING
                y = init_top_left_y + INITIAL_Y_PADDING + BDO_ITEM_SQUARE_HEIGHT + BDO_ITEM_SQUARE_PADDING * 2 + 1
            square_detection = {
                "TOP_LEFT_X": x,
                "TOP_LEFT_Y": y,
                "BOTTOM_RIGHT_X": x + BDO_ITEM_SQUARE_WIDTH,
                "BOTTOM_RIGHT_Y": y + BDO_ITEM_SQUARE_HEIGHT,
                "MATCH_VALUE": 0,
                "LABEL": i,
                "COLOR": (0, 0, 255),
            }
            # Save the detected item's values (Currently used for debugging, may be useful in the future)
            self._squares.append(square_detection)
            # Save the detected item's icon
            self._square_img.append(image_with_detections[y:y + BDO_ITEM_SQUARE_HEIGHT, x:x + BDO_ITEM_SQUARE_WIDTH])
            # Go to next square's top left corner
            x += BDO_ITEM_SQUARE_WIDTH + BDO_ITEM_SQUARE_PADDING * 2 + 1
        # Outline the squares on the image (OPTIONAL, for debugging.)
        for detection in self._squares:
            self.drawSquareAroundDetection(detection, image_with_detections)
        # Go over each square and match it to the templates
        self.matchItemToTemplates()
            

    def readCroppedImage(self, img):
        """WIP Function to read data written in the image.

        Args:
            img ([2d/3d matrix]): [represents an image]
        """
        ret,thresh1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(thresh1)
        print(f"Detected integers in the image: {''.join(filter(str.isdigit, text))}")

    def matchItemToTemplates(self):
        """Test function for now! go over loot table and compare with acquired loot.
        """
        ronaros_loot_table = [
            Template(
                    image_path="templates/ronaros_drops/bs_armor.png", label=r"Black Stone Armor", color=(125, 0, 255)
            ),
            Template(
                    image_path="templates/ronaros_drops/caphra.png", label=r"Caphra's Stone", color=(125, 0, 255)
            ),
            Template(
                    image_path="templates/ronaros_drops/forest_fury.png", label=r"Forest Fury", color=(125, 0, 255)
            ),
            Template(
                    image_path="templates/ronaros_drops/guardian_stone.png", label=r"Guardian Life Stone", color=(125, 0, 255)
            ),
            Template(
                    image_path="templates/ronaros_drops/lem_gloves.png", label=r"Lemoria Gloves", color=(125, 0, 255)
            ),
            Template(
                    image_path="templates/ronaros_drops/manshaum_doll.png", label=r"Manshaum Doll", color=(125, 0, 255)
            ),
            Template(
                    image_path="templates/ronaros_drops/pure_forest_breath.png", label=r"Pure Forest Breath", color=(125, 0, 255)
            ),
            Template(
                    image_path="templates/ronaros_drops/ronaros_ring.png", label=r"Ronaros Ring", color=(125, 0, 255)
            ),
            Template(
                    image_path="templates/ronaros_drops/rumbling_earth_shard.png", label=r"Rumbling Earth Shard", color=(125, 0, 255)
            ),
        ]
        i = 0
        for image in self._square_img:
            i += 1
            match_dict = {}
            for template in ronaros_loot_table:
                percentage = self.calculateImageResemblance(image,template.template) * 100
                match_dict[template.label] = percentage
            print(f"\n\n\nItem num: {i}\nBest match: {max(match_dict, key=lambda key: match_dict[key])}\n")
            # for key, value in match_dict.items():
                # print(f"{key}: {value}%")

    def calculateImageResemblance(self, image1, image2):
        """Calculates the similarity of image1 and image2

        Args:
            image1 ([2d/3d matrix]): [represents an image]
            image2 ([2d/3d matrix]): [represents an image]

        Returns:
            [int]: [image similarity (0-1) where 1 is similar and 0 is different]
        """
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        return ssim(cv2.resize(image1, (50,50)), cv2.resize(image2, (50,50)), multichannel=True)

# TODO: To get a precise location of the item frame, we'll have to go over multiple different templates, they will share location of the desired 'real' item, might be a bit heavy on the processing but will add higher % of success.
