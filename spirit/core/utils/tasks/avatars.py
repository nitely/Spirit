# -*- coding: utf-8 -*-

import io

from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image


def crop_max_square(image):
    """Return maximum centered square"""
    w, h = image.size
    wh = min(w, h)
    x = max(0, (w - wh) // 2)
    y = max(0, (h - wh) // 2)
    return image.crop((x, y, x+wh, y+wh))


def resize_max(image, to):
    """Return downscaled image if needed"""
    assert min(image.size) == max(image.size), 'not a square'
    if max(image.size) <= to:
        return image
    return image.resize((to, to), resample=Image.BICUBIC)


def to_file(image):
    """Return Django file"""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    buff = io.BytesIO()
    image.save(buff, format='JPEG', subsampling=0, quality=90)
    return SimpleUploadedFile(
        'pic.jpg', content=buff.getvalue(), content_type='image/jpeg')


def thumbnail(image, to):
    """Return Django file of downscaled image"""
    return to_file(resize_max(image, to))
