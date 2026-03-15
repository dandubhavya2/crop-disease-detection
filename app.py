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

    file = request.files["image"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    img = cv2.imread(path)
    img = cv2.resize(img, (300,300))

    # Convert image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Detect dark/brown disease spots
    lower_spot = np.array([0,40,40])
    upper_spot = np.array([180,255,120])

    mask = cv2.inRange(hsv, lower_spot, upper_spot)

    # Remove noise
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Highlight infected area
    result_img = img.copy()
    result_img[mask == 255] = [0,0,255]

    result_path = os.path.join("static","result.png")
    cv2.imwrite(result_path, result_img)

    # Calculate disease percentage
    disease_pixels = np.sum(mask==255)
    total_pixels = mask.size

    percent = (disease_pixels/total_pixels)*100

    # Classification
    if percent < 1:
        result = "Healthy Leaf"
        disease = "No Disease"
    elif percent < 8:
        result = "Diseased Leaf"
        disease = "Leaf Spot Disease"
    else:
        result = "Severely Diseased Leaf"
        disease = "Leaf Blight"

    return render_template(
        "result.html",
        result=result,
        disease=disease,
        percent=round(percent,2),
        image="result.png"
    )


import os
if _name_ == "_main_":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)