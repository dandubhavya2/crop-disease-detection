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
        result = "Leaf is Diseased"
    else:
        result = "Leaf is Healthy"

    return render_template("result.html", result=result)


if _name_ == '_main_':
    app.run(debug=True)