from flask import Flask, render_template, request
import cv2
import numpy as np
import os

app = Flask(_name_)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    file = request.files["image"]
    if file.filename == '':
        return "No file selected", 400
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    img = cv2.imread(path)
    img = cv2.resize(img, (300, 300))  # Keep for speed, but consider larger for accuracy

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Tighter brown/dark spot range (common for leaf spots/blight) [web:2]
    lower_spot = np.array([8, 60, 20])
    upper_spot = np.array([30, 255, 200])
    mask_spot = cv2.inRange(hsv, lower_spot, upper_spot)

    # First, segment green leaf (helps focus calculation)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    mask_leaf = cv2.inRange(hsv, lower_green, upper_green)

    # Morphology for both
    kernel = np.ones((7, 7), np.uint8)  # Larger kernel for better cleaning
    mask_spot = cv2.morphologyEx(mask_spot, cv2.MORPH_OPEN, kernel)
    mask_spot = cv2.morphologyEx(mask_spot, cv2.MORPH_CLOSE, kernel)
    mask_leaf = cv2.morphologyEx(mask_leaf, cv2.MORPH_OPEN, kernel)

    # Find largest leaf contour
    contours_leaf, _ = cv2.findContours(mask_leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours_leaf:
        return render_template("result.html", result="No leaf detected", disease="Error", percent=0, image="")

    largest_leaf = max(contours_leaf, key=cv2.contourArea)
    mask_leaf = np.zeros_like(mask_leaf)
    cv2.fillPoly(mask_leaf, [largest_leaf], 255)

    # Disease pixels only within leaf
    disease_pixels = np.sum((mask_spot == 255) & (mask_leaf == 255))
    leaf_pixels = np.sum(mask_leaf == 255)
    if leaf_pixels == 0:
        percent = 0
    else:
        percent = (disease_pixels / leaf_pixels) * 100

    # Highlight only on leaf/spot
    result_img = img.copy()
    result_img[mask_spot == 255] = [0, 0, 255]  # Red for spots

    result_path = os.path.join("static", "result.png")
    cv2.imwrite(result_path, result_img)

    # Adjusted thresholds (tune based on your dataset)
    if percent < 2:
        result = "Healthy Leaf"
        disease = "No Disease"
    elif percent < 15:
        result = "Diseased Leaf"
        disease = "Leaf Spot Disease"
    else:
        result = "Severely Diseased Leaf"
        disease = "Leaf Blight"

    return render_template(
        "result.html",
        result=result,
        disease=disease,
        percent=round(percent, 2),
        image="result.png"
    )