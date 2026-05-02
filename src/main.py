import os
from dotenv import load_dotenv
import argparse
import yaml
import logging

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
