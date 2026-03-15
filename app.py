from flask import Flask, render_template, request
import cv2
import numpy as np
import os

app = Flask(_name_)

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
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)

    _, thresh = cv2.threshold(blur,120,255,cv2.THRESH_BINARY_INV)

    disease_pixels = np.sum(thresh==255)
    total_pixels = thresh.size

    percent = (disease_pixels/total_pixels)*100

    if percent > 5:
       …
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
    img = cv2.resize(img,(300,300))

    # convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # detect yellow areas
    lower_yellow = np.array([20,100,100])
    upper_yellow = np.array([35,255,255])

    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # detect dark spots
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, dark_mask = cv2.threshold(gray,80,255,cv2.THRESH_BINARY_INV)

    # count pixels
    yellow_pixels = np.sum(yellow_mask==255)
    dark_pixels = np.sum(dark_mask==255)

    # decision rule
    if yellow_pixels > 1200 or dark_pixels > 1500:
        result = "Diseased Leaf"
    else:
        result = "Healthy Leaf"

    return render_template("result.html", result=result)


import os
if _name_ == "_main_":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)