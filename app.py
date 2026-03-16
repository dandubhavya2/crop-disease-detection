
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
    #mask for diseased dark/brown regions
    lower_brown = np.array([25,40,40])
    upper_brown= np.array([90,255,255])

    leaf_mask = cv2.inRange(hsv,lower_brown,upper_brown)
   #remove noise
    kernel = np.ones((5,5),np.uint8)
    disease_mask = cv2.morphologyEx(leaf_mask,cv2.MORPH_OPEN,kernel)
    disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_OPEN, kernel)

    #count pixels
    leaf_pixels = cv2.countNonZero(leaf_mask)
    disease_pixels = cv2.countNonZero(disease_mask)

    # calculate percentage
    percent = (disease_pixels / (leaf_pixels+disease_pixels)) * 100
    percent = round(percent,2)

    if percent > 3:
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
    app.run(debug=True)