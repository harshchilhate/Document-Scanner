import os
from dotenv import load_dotenv
import yaml
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    with open("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    logger.error("config.yaml not found")
    exit(1)
except yaml.YAMLError as e:
    logger.error(f"Error reading config.yaml : {e}")
    exit(1)
