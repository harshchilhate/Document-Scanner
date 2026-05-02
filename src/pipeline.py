import os
from dotenv import load_dotenv
import cv2
import yaml
import numpy as np
import logging

logger = logging.getLogger(__name__)

# 1. load_image(image_path)
#    - cv2.imread()
#    - if image is None → log error, return None
def load_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Image not found at path: {image_path}")
            return None
        return image
    except Exception as e:
        logger.error(f"Failed to read image: {e}")
        return None
    

# 2. validate_image(image, file_path)
#    - check format is JPEG, JPG, PNG or WEBP
#    - check resolution is within 240×144 and 3840×2160
#    - if invalid → log error, return False
def validate_image(image, file_path):
    valid_image_format = [".jpeg", ".png", ".webp", ".jpg"]
    height, width = image.shape[:2]
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    try: 
        if ext not in valid_image_format:
            logger.error(f"Given image type is not supported.")
            return False
        if width < 240 or width > 3840 or height < 144 or height > 2160:
            logger.error(f"Given image size {image.shape[0]}x{width} is not supported.")
            return False
        return True
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False


# 3. preprocess_image(image, config)
#    - convert to grayscale with cvtColor
#    - apply GaussianBlur using kernel size from config
#    - return processed image
def preprocess_image(image, config):
    try:
        kernel_size = config["gaussian"]["kernel_size"]
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_gray_image = cv2.GaussianBlur(gray_image, (kernel_size, kernel_size), 0)
        return blurred_gray_image
    except Exception as e:
        logger.error(f"Preprocessing failed : {e}")
        return None


# 4. detect_edges(image, config)
#    - apply cv2.Canny using thresholds from config
#    - return edge map
def detect_edges(blurred_gray_image, config):
    try:
        threshold1 = config["canny"]["threshold1"]
        threshold2 = config["canny"]["threshold2"]
        edges = cv2.Canny(blurred_gray_image, threshold1, threshold2)
        return edges
    except Exception as e:
        logger.error(f"Edge detection failed: {e}")
        return None


# 5. find_document_contour(edges, image, config)
#    - cv2.findContours
#    - cv2.approxPolyDP to get polygons
#    - keep only 4-point polygons
#    - filter by min_area_ratio from config
#    - return largest valid contour
def find_document_contour(edges, image, config):
    try:
        min_area_ratio = config["contour"]["min_area_ratio"]
        image_area = image.shape[0] * image.shape[1]
        
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            logger.error("No contours found in image")
            return None
        
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for contour in contours:
            # 1. Calculate the area
            area = cv2.contourArea(contour)
            if area < min_area_ratio * image_area:
                continue

            # 2. Derive epsilon from area
            epsilon = 0.02 * cv2.arcLength(contour, True)

            # 3. Apply the approximation
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if  len(approx) ==4 :
                return approx
        logger.error("No valid document contour found")
        return None
    
    except Exception as e:
        logger.error(f"Contour detection faild : {e}")
        return None


# 6. order_points(contour)
#    - sort corners into TL, TR, BR, BL order
#    - return ordered array of 4 points
def order_points(contour):
    try:
        points = contour.reshape(4, 2).astype("float32")
        ordered = np.zeros((4, 2), dtype="float32")

        sums = []
        diffs = []
        for point in points:
            sums.append(point[0] + point[1])   # x + y
            diffs.append(point[0] - point[1])  # x - y

        ordered[0] = points[sums.index(min(sums))]   # TL → smallest sum
        ordered[2] = points[sums.index(max(sums))]   # BR → largest sum
        ordered[1] = points[diffs.index(min(diffs))] # TR → smallest diff
        ordered[3] = points[diffs.index(max(diffs))] # BL → largest diff

        return ordered
    except Exception as e:
        logger.error(f"Ordering points failed: {e}")
        return None


# 7. transform_perspective(image, ordered_points)
#    - compute output dimensions
#    - cv2.getPerspectiveTransform
#    - cv2.warpPerspective
#    - return warped image
def transform_perspective(image, ordered):
    try:
        TL = ordered[0]
        TR = ordered[1]
        BR = ordered[2]
        BL = ordered[3]

        # compute width
        width1 = np.sqrt(((BR[0] - BL[0]) ** 2) + ((BR[1] - BL[1]) ** 2))
        width2 = np.sqrt(((TR[0] - TL[0]) ** 2) + ((TR[1] - TL[1]) ** 2))
        width = int(max(width1, width2))

        # compute height
        height1 = np.sqrt(((TR[0] - BR[0]) ** 2) + ((TR[1] - BR[1]) ** 2))
        height2 = np.sqrt(((TL[0] - BL[0]) ** 2) + ((TL[1] - BL[1]) ** 2))
        height = int(max(height1, height2))

        # source and destination points
        source = np.array([TL, TR, BR, BL], dtype="float32")
        destination = np.array([
            [0, 0],
            [width, 0],
            [width, height],
            [0, height]
        ], dtype="float32")

        # apply transform
        matrix = cv2.getPerspectiveTransform(source, destination)
        warped = cv2.warpPerspective(image, matrix, (width, height))

        return warped
    except Exception as e:
        logger.error(f"Perspective transform failed: {e}")
        return None


# 8. postprocess_image(image)
#    - cv2.adaptiveThreshold
#    - return cleaned image
def postprocess_image(image):
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        final_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 3)
        return final_image
    except Exception as e:
        logger.error(f"Postprocessing failed: {e}")
        return None


# 9. save_image(image, input_path, config)
#    - build output filename using prefix from config
#    - save to OUTPUT_PATH from .env
#    - log success message