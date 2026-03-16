
from flask import Flask, render_template, request
import cv2
import numpy as np
import os

app = Flask(__name__)

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
    if img is None:
        return "Image not loaded.Please upload a valid image"
    img = cv2.resize(img,(400,400))

    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    #healthy green color range
    lower_green=np.array([25,40,40])
    upper_green=np.array([90,255,255])

    # for diseased dark/brown regions
    lower_brown = np.array([102,602,202])
    upper_brown=np.array([902,255,200])
    # masks
    green_mask=cv2.inRange(hsv,lower_green,upper_green)
    brown_mask=cv2.inRange(hsv,lower_brown,upper_brown)
    kernel=np.ones((5,5),np.uint8)

    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    brown_mask = cv2.morphologyEx(brown_mask, cv2.MORPH_OPEN, kernel)

    leaf_pixels = cv2.countNonZero(green_mask)
    disease_pixels = cv2.countNonZero(brown_mask)

    total_pixels = leaf_pixels + disease_pixels

    if total_pixels == 0:
        percent = 0
    else:
        percent = (disease_pixels / total_pixels) * 100

    percent = round(percent,2)

    if percent > 15:
        result = "Diseased Leaf"
    else:
        result = "Healthy Leaf"

    return render_template(
        "result.html",
        result=result,
        percent=percent,
        image=path
    )
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=True)