# app.py
import json
import os

from math import floor
from scripts.trained_resnet import MyModel
from flask import Flask, request, jsonify, render_template


# initialize flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# declare constants
img_class_map = None
with open('scripts/index_to_class_label.json') as f:
    img_class_map = json.load(f)


def load_model():
    """Retrieves the trained model and maps it to the CPU by default,
    can also specify GPU here."""
    model_cnn = MyModel("models/pre-trained_CNN.pth", "cpu")
    return model_cnn


def render_prediction(index):
    stridx = str(index)
    class_name = 'Unknown'
    if img_class_map is not None:
        if stridx in img_class_map is not None:
            class_name = img_class_map[stridx]
    return class_name


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/infer', methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        saveLocation = f.filename
        f.save(saveLocation)
        model = load_model()
        inference, confidence = model.infer(saveLocation)
        class_name = render_prediction(inference)
        # make a percentage with 2 decimal points
        confidence = floor(confidence * 10000) / 100
        # delete file after making an inference
        os.remove(saveLocation)
        return render_template('inference.html', name=class_name,
                               confidence=confidence)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
