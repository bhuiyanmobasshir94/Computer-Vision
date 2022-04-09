import base64
import os
from io import BytesIO, StringIO
from pprint import pprint

import easyocr
import pandas as pd
from PIL import Image

import streamlit as st

bn_reader = easyocr.Reader(['bn'], gpu=True)
en_reader = easyocr.Reader(['en'], gpu=True)


def get_nid_image(image_url):
    image_data = base64.b64decode(image_url)
    image_data = BytesIO(image_data)
    image = Image.open(image_data)
    return image


def get_nid_text(front_image, back_image):
    bn_front = bn_reader.readtext(front_image, detail=0, paragraph=False)
    en_front = en_reader.readtext(front_image, detail=0, paragraph=False)
    bn_back = bn_reader.readtext(back_image, detail=0, paragraph=True)
    en_back = en_reader.readtext(back_image, detail=0, paragraph=True)
    # nid_pattern = "[0-9]{3} [0-9]{3} [0-9]{4}"
    # dob_pattern = "^Date of Bir"
    # name_pattern = "[A-Z]* [A-Z]* [A-Z]*"
    for index, phrase in enumerate(bn_front):
        if phrase == 'নাম':
            bn_name = bn_front[index + 1]
        elif phrase == 'পিতা':
            bn_father_name = bn_front[index + 1]
        elif phrase == 'মাতা':
            bn_mother_name = bn_front[index + 1]

    for index, phrase in enumerate(en_front):
        if phrase == 'Name':
            en_name = en_front[index + 1]
        elif phrase == 'Date of Birth':
            en_dob = en_front[index + 1]
        elif phrase == 'NID No':
            en_nid = en_front[index + 1]

    response = {
        "bn_name": bn_name,
        "en_name": en_name,
        "bn_father_name": bn_father_name,
        "bn_mother_name": bn_mother_name,
        "en_dob": en_dob,
        "en_nid": en_nid,
        "bn_address": bn_back[0],
        "en_birth_place": en_back[2],
        "en_issue_date": en_back[3]
    }
    # pprint(response, indent=4)
    return response


with st.form("nid_scanner_form", clear_on_submit=True):
    front_image = st.file_uploader("Front Image", type=["jpg", "png", "jpeg"])
    back_image = st.file_uploader("Back Image", type=["jpg", "png", "jpeg"])
    submit = st.form_submit_button("Submit")
    if submit:
        if front_image is not None and back_image is not None:
            front_image_ext = os.path.splitext(front_image.name)[
                1].replace(".", "")
            back_image_ext = os.path.splitext(back_image.name)[
                1].replace(".", "")
            front_image_bytes = front_image.getvalue()
            back_image_bytes = back_image.getvalue()
            front_image_base64 = base64.b64encode(
                front_image_bytes).decode("utf-8")
            back_image_base64 = base64.b64encode(
                back_image_bytes).decode("utf-8")
            front_image_data = f"data:image/{front_image_ext};base64," + \
                front_image_base64
            back_image_data = f"data:image/{back_image_ext};base64," + \
                back_image_base64
            st.image(front_image_data, caption="Front Image")
            st.image(back_image_data, caption="Back Image")
            front_str_to_img = Image.open(BytesIO(base64.b64decode(
                front_image_base64)))
            back_str_to_img = Image.open(BytesIO(base64.b64decode(
                back_image_base64)))
            try:
                response = get_nid_text(front_str_to_img, back_str_to_img)
                st.code(response, language="json")
            except Exception as e:
                st.error(e)
        else:
            st.error("Please upload both images in order to proceed")
