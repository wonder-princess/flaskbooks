from pathlib import Path

import cv2
import numpy as np
import PIL
import torch
from flask import current_app, jsonify
from flaskbook_api.api.postprocess import (draw_lines, draw_texts, make_color,
                                           make_line)
from flaskbook_api.api.preparation import load_image
from flaskbook_api.api.preprocess import image_to_tensor

basedir = Path(__file__).parent.parent

def detection(request):
    dict_results = {}
    labels = current_app.config["LABELS"]
    image, filename = load_image(request)
    image_tensor = image_to_tensor(image)

    try:
        model = torch.load("mode.pt")
    except FileNotFoundError:
        return jsonify("The model is not found"), 404

    model = model.eval()
    output = model([image_tensor])[0]

    result_image = np.array(image.copy())

    for box, label, score in zip(output["boxes"], output["labels"], output["scores"]):
        if score > 0.6 and labels[label] not in dict_results:
            color = make_color(labels)
            line = make_line(result_image)
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))

            draw_lines(c1, c2, result_image, line, color)
            draw_texts(result_image, line, c1, cv2, color, labels[label])

        dir_image = str(basedir / "data" / "orijinal" / filename)
        cv2.imwrite(dir_image, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))
    return jsonify(dict_results), 201

def detection_alt():
    print("----------")

    dict_results = {}
    labels = current_app.config["LABELS"]
    filename = "test.jpg"

    dir_image = str[basedir / "data" / "orijinal" / filename]
    image_obj = PIL.Image.open(dir_image.convert('RGB'))
    image = image_obj.resize(reshaped_size=(256,256))

    image_tensor = image_to_tensor(image)

    try:
        model = torch.load("mode.pt")
    except FileNotFoundError:
        return jsonify("The model is not found"), 404

    model = model.eval()
    output = model([image_tensor])[0]

    result_image = np.array(image.copy())

    for box, label, score in zip(output["boxes"], output["labels"], output["scores"]):
        if score > 0.6 and labels[label] not in dict_results:
            color = make_color(labels)
            line = make_line(result_image)
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))

            draw_lines(c1, c2, result_image, line, color)
            draw_texts(result_image, line, c1, cv2, color, labels[label])

        dir_image = str(basedir / "data" / "orijinal" / filename)
        cv2.imwrite(dir_image, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))
    return jsonify(dict_results), 201
