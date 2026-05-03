import os
from dotenv import load_dotenv
import argparse
import yaml
import logging
from pipeline import (
    load_image,
    validate_image,
    preprocess_image,
    detect_edges,
    find_document_contour,
    order_points,
    transform_perspective,
    postprocess_image,
    save_image
)

# logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


#get INPUT_PATH from .env
load_dotenv()
base_path = os.getenv("INPUT_PATH")
if base_path is None:
    logging.error("INPUT_PATH not set in .env")
    exit(1)

# load config
try:
    with open("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    logger.error("config.yaml not found")
    exit(1)
except yaml.YAMLError as e:
    logger.error(f"Error reading config.yaml : {e}")
    exit(1)

#get image name from CLI
ap = argparse.ArgumentParser()
ap.add_argument("--image", required=True, help="filename of input image e.g. document.jpg")
args = ap.parse_args()

file_name = args.image


#counstruct full path
full_path = os.path.join(base_path, file_name)
logger.info(f"Input path: {full_path}")

#get path from OUTPUT_PATH 
output_path = os.getenv("OUTPUT_PATH")
file_name = os.path.splitext(args.image)[0]

def main():
    image = load_image(full_path)
    if image is None:
        exit(1)

    if not validate_image(image, full_path):
        exit(1)

    original = image.copy()

    preprocessed = preprocess_image(image, config)
    if preprocessed is None:
        exit(1)

    edges = detect_edges(preprocessed, config)
    if edges is None:
        exit(1)

    contour = find_document_contour(edges, image, config)
    if contour is None:
        exit(1)

    ordered = order_points(contour)
    if ordered is None:
        exit(1)

    warped = transform_perspective(original, ordered)
    if warped is None:
        exit(1)

    cleaned = postprocess_image(warped)
    if cleaned is None:
        exit(1)

    save_image(cleaned, file_name, output_path, config)
    logger.info("Pipeline completed successfully")

if __name__ == "__main__":
    main()