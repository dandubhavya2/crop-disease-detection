
from flask import Flask, render_template, request
import cv2
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/detect', methods=['POST'])
def detect():

    file = request.files['image']
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    img = cv2.imread(path)
    img = cv2.resize(img,(300,300))

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_brown = np.array([5,50,50])
    upper_brown = np.array([30,255,255])

    mask = cv2.inRange(hsv, lower_brown, upper_brown)

    highlight = img.copy()
    highlight[mask == 255] = [0,0,255]

    result_image = os.path.join("static","result.png")
    cv2.imwrite(result_image, highlight)

    disease_pixels = np.sum(mask==255)
    total_pixels = mask.size

    percent = (disease_pixels/total_pixels)*100

    if percent < 2:
        result = "Healthy Leaf"
        disease = "No Disease"
    elif percent < 10:
        result = "Diseased Leaf"
        disease = "Leaf Spot"
    else:
        result = "Severely Diseased Leaf"
        disease = "Blight Infection"

    return render_template(
        "result.html",
        result=result,
        disease=disease,
        percent=round(percent,2),
        image="result.png"
    )

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
