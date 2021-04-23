from cv2 import cv2
import numpy as np
from singleton import Singleton
from pathlib import Path

DEFAULT_TEMPLATE_MATCHING_THRESHOLD = 0.5
NMS_THRESHOLD = 0.2
OUTPUT_FILE_PATH = f"output/result.jpeg"


class Template:
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

class ImageProcessingManager(metaclass=Singleton):
    def __init__(self, image_path = "input_image/test.png", templates = None):
        self._image = cv2.imread(image_path) #Image to apply the templates on.
        if templates is None:
            self._templates = [
                # Template(image_path="vin.png", label="1", color=(0, 0, 255)),
                #Template(image_path="vintest.png", label="2", color=(0, 255, 0)),
                # Template(image_path="vinegar2.png", label="3", color=(0, 255, 255)),
                Template(image_path="templates/vinegar3.png", label="4", color=(125, 0, 255)),
                # Template(image_path="vinegar4.png", label="5", color=(125, 255, 125)),
            ]
        self._detections = []

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
        try:
            for template in self._templates:
                template_matching = cv2.matchTemplate(
                template.template, self._image, cv2.TM_CCOEFF_NORMED
                )

                match_locations = np.where(template_matching >= template.matching_threshold)

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
            self._detections = self.non_max_suppression(
                self._detections, non_max_suppression_threshold=NMS_THRESHOLD
            )
            image_with_detections = self._image.copy()
            for detection in self._detections:
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
            Path('output').mkdir(parents=True, exist_ok=True) # Create output folder in case it doesn't exist.
            cv2.imwrite(OUTPUT_FILE_PATH, image_with_detections)
        except Exception as e:
            print(e)
        else:
            print(f"Successfully processed the image. The output is located at: {OUTPUT_FILE_PATH}")

#TODO: To get a precise location of the item frame, we'll have to go over multiple different templates, they will share location of the desired 'real' item, might be a bit heavy on the processing but will add higher % of success.
