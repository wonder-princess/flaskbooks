import random
import uuid
from pathlib import Path
from unittest import result

import cv2
import numpy as np
import torch
import torchvision
from apps.app import db
from apps.crud.models import User
from apps.detector.forms import DeleteForm, DetectorForm, UploadImageForm
from apps.detector.models import UserImage, UserImageTag
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, send_from_directory, url_for)
from flask_login import current_user, login_required
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError

dt = Blueprint(
    "detector",
    __name__,
    template_folder="templates",
)

@dt.route("/")
def index():

    user_images = (db.session.query(User, UserImage).join(UserImage).filter(User.id == UserImage.user_id).all())

    user_images_tag_dict = {}
    for user_image in user_images:
        user_image_tags = (
            db.session.query(UserImageTag).filter(UserImageTag.user_image_id == user_image.UserImage.id).all()
        )
        user_images_tag_dict[user_image.UserImage.id] = user_image_tags

    detector_form = DetectorForm()
    delete_form = DeleteForm()

    return render_template(
        "detector/index.html",
        user_images=user_images,
        user_image_tag_dict=user_images_tag_dict,
        detector_form=detector_form,
        delete_form=delete_form
        )

@dt.route("/images<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@dt.route("/upload", methods=["GET", "POST"])
@login_required
def upload_image():
    form = UploadImageForm()
    if form.validate_on_submit():
        file = form.image.data
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext

        image_path = Path(
            current_app.config["UPLOAD_FOLDER"], image_uuid_file_name
        )
        file.save(image_path)

        user_image = UserImage(
            user_id=current_user.id, image_path=image_uuid_file_name
        )
        db.session.add(user_image)
        db.session.commit()

        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)

def make_color(labels):
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color

def make_line(result_image):
    line = round(0.002 * max(result_image.shape[0:2])) + 1
    return line

def dralw_lines(c1, c2, result_image, line, color):

    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2

def dralw_texts(result_image, line, c1, cv2, color, labels, label):
    
    display_txt = f"{labels[label]}" 
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(
        display_txt, 0, fontScale=line / 3, thickness=font
    )[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] -3

    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] -2),
        0,
        line / 3,
        [255, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )
    return cv2

def exec_detector(target_image_path):
    labels = current_app.config["LABELS"]
    image = Image.open(target_image_path)
    image_tensor = torchvision.transforms.functional.to_tensor(image)
    model = torch.load(Path(current_app.root_path, "detector", "model.pt"))
    model = model.eval()
    output = model([image_tensor])[0]
    tags = []

    cv2 = None

    result_image = np.array(image.copy())
    for box, label, score in zip(output["boxes"], output["labels"], output["scores"]):
        if score > 0.5 and labels[label] not in tags:
            color = make_color(labels)
            line = make_line(result_image)
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))
            cv2 = dralw_lines(c1, c2, result_image, line, color)
            cv2 = dralw_texts(result_image, line, c1, cv2, color, labels, label)
            tags.append(labels[label])
    
    detected_image_file_name = str(uuid.uuid4()) + ".jpg"
    deteted_image_file_path = str(Path(current_app.config["UPLOAD_FOLDER"], detected_image_file_name))
    cv2.imwrite(deteted_image_file_path, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))
    return tags, detected_image_file_name

def save_detected_image_tags(user_image, tags, detected_image_file_name):
    user_image.image_path = detected_image_file_name
    user_image.is_detected = True
    db.session.add(user_image)

    for tag in tags:
        user_image_tag = UserImageTag(user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)
        db.session.commit()

@dt.route("/detect/<string:image_id>", methods=["POST"])
@login_required
def detect(image_id):
    user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()
    if user_image is None:
        flash("物体検知対象の画像が存在しません。")
        return redirect(url_for("detector.index"))

    target_image_path = Path(current_app.config["UPLOAD_FOLDER"], user_image.image_path)
    tags, detected_image_file_name = exec_detector(target_image_path)

    try:
        save_detected_image_tags(user_image, tags, detected_image_file_name)
    except SQLAlchemyError as e:
        flash("物体検知処理でエラーが発生しました。")
        db.session.rollback()
        current_app.logger.error(e)
        return redirect (url_for("detector.index"))
    return redirect(url_for("detector.index"))
    
@dt.route("/images/delete/<string:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    try:
        db.session.query(UserImageTag).filter(UserImageTag.user_image_id == image_id).delete()
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        flash("画像削除処理でエラーが発生しました。")
        current_app.logger.error(e)
        db.session.rollback()

    return redirect(url_for("detector.index"))

@dt.route("/images/serch", methods=["GET"])
def search():
    user_images = db.session.query(User,UserImage).join(UserImage, User.id == UserImage.user_id)

    search_text = request.args.get("search")
    user_image_tag_dict = {}
    filtered_user_images = []

    for user_image in user_images:
        if not search_text:
            user_image_tags = (
                db.session.query(UserImageTag).filter(UserImageTag.user_image_id == user_image.UserImage.id).all()
            )
        else:
            user_image_tags = (
                db.session.query(UserImageTag).filter(UserImageTag.user_image_id == user_image.UserImage.id).filter(UserImageTag.tag_name.like("%" + search_text + "%")).all()
            )
            
            if not user_image_tags:
                continue

            user_image_tags = (
                db.session.query(UserImageTag).filter(UserImageTag.user_image_id == user_image.UserImage.id).all()
            )

        #未実装時の挙動を確認
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

        filtered_user_images.append(user_image)

    delete_form = DeleteForm()
    detector_form = DetectorForm()

    return render_template(
        "detector/index.html",
        user_images=filtered_user_images,
        user_image_tag_dict=user_image_tag_dict,
        delete_form=delete_form,
        detector_form=detector_form,
    )

@dt.errorhandler(404)
def page_not_found(e):
    return render_template("detector/404.html"),404
