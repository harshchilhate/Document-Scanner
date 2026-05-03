import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import (
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
from dotenv import load_dotenv
import yaml
import cv2

load_dotenv()

with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# ── Test 1 ──────────────────────────────────────────
def test_load_invalid_path():
    result = load_image("fake/path/image.jpg")
    if result is None:
        print("PASS: test_load_invalid_path")
    else:
        print("FAIL: test_load_invalid_path")

# ── Test 2 ──────────────────────────────────────────
def test_validate_invalid_format():
    sample = load_image("samples/Doc1.jpeg")
    result = validate_image(sample, "samples/Doc1.gif")
    if result is False:
        print("PASS: test_validate_invalid_format")
    else:
        print("FAIL: test_validate_invalid_format")

# ── Test 3 ──────────────────────────────────────────
def test_full_pipeline_on_sample():
    image = load_image("samples/Doc1.jpeg")
    if image is None:
        print("FAIL: test_full_pipeline - could not load image")
        return

    if not validate_image(image, "samples/Doc1.jpeg"):
        print("FAIL: test_full_pipeline - validation failed")
        return

    original = image.copy()
    preprocessed = preprocess_image(image, config)
    edges = detect_edges(preprocessed, config)
    contour = find_document_contour(edges, image, config)
    if contour is None:
        print("FAIL: test_full_pipeline - no contour found")
        return

    ordered = order_points(contour)
    warped = transform_perspective(original, ordered)

    h, w = warped.shape[:2]
    if h < w:
        warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)
    warped = cv2.flip(warped, 1)

    cleaned = postprocess_image(warped)
    
    output_path = os.getenv("OUTPUT_PATH")
    save_image(cleaned, "Doc1", output_path, config)

    output_file = os.path.join(output_path, "processed_Doc1.png")
    if os.path.exists(output_file):
        print("PASS: test_full_pipeline_on_sample")
    else:
        print("FAIL: test_full_pipeline - output file not saved")

# ── Run All Tests ────────────────────────────────────
if __name__ == "__main__":
    print("\nRunning tests...\n")
    test_load_invalid_path()
    test_validate_invalid_format()
    test_full_pipeline_on_sample()
    print("\nDone.")