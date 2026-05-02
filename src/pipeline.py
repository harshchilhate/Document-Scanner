import os
import cv2
import yaml
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

# 5. find_document_contour(edges, image, config)
#    - cv2.findContours
#    - cv2.approxPolyDP to get polygons
#    - keep only 4-point polygons
#    - filter by min_area_ratio from config
#    - return largest valid contour

# 6. order_points(contour)
#    - sort corners into TL, TR, BR, BL order
#    - return ordered array of 4 points

# 7. transform_perspective(image, ordered_points)
#    - compute output dimensions
#    - cv2.getPerspectiveTransform
#    - cv2.warpPerspective
#    - return warped image

# 8. postprocess_image(image)
#    - cv2.adaptiveThreshold
#    - return cleaned image

# 9. save_image(image, input_path, config)
#    - build output filename using prefix from config
#    - save to OUTPUT_PATH from .env
#    - log success message