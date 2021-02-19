
from gallery.models import Album, AlbumImage, ImageTag, TagMapping
from django.core.files.base import ContentFile
import config.settings

from PIL import Image

# Importing Pillow Python Imaging Library:that adds support for opening, manipulating, and saving many different image file formats.
import PIL.ExifTags
import os, sys
import uuid
import zipfile

from datetime import datetime
from zipfile import ZipFile
from pathlib import Path
from fractions import Fraction

def processimages(zipname, album):
    exifAttrs = set(["ImageDescription", "XPKeywords"])

    if zipname != None:
        zip = zipfile.ZipFile(zipname)
        for filename in sorted(zip.namelist()):

            file_name = os.path.basename(filename)
            if not file_name:
                continue

            data = zip.read(filename)
            contentfile = ContentFile(data)

            img = AlbumImage()
            img.album = album
            img.alt = filename
            newfilename = '{0}{1}.jpg'.format(album.slug, str(uuid.uuid4())[-13:])
            img.image.save(newfilename, contentfile)

            thumbfilename = 'thumb-{0}{1}.jpg'.format(album.slug, str(uuid.uuid4())[-13:])
            img.thumb.save(thumbfilename, contentfile)

            filepath = '{0}/albums/{1}'.format(config.settings.MEDIA_ROOT, newfilename)
            with Image.open(filepath) as i:
                img.width, img.height = i.size

            with Image.open(contentfile) as i:
                exif_data_PIL = i.getexif()
                exif_data = {}
                for k, v in PIL.ExifTags.TAGS.items():
                    decodedAttr = PIL.ExifTags.TAGS.get(k, k)
                    if decodedAttr in exifAttrs:
                        if k in exif_data_PIL:
                            value = exif_data_PIL[k]
                            exif_data[v] = {"tag": k,
                                            "raw": value,
                                            "processed": value}

                if exif_data != {}:
                    _process_exif_dict(exif_data)
                    img.title = _get_field(exif_data, 'ImageDescription')
                    tags = _get_field(exif_data, 'XPKeywords')
                    if tags != "":
                        _process_tags(tags, img)

            img.save()

        

def _get_field (exif, field):
    try:
        subvalue = exif[field]
        return subvalue["processed"]
    except KeyError:
        return ""


def _process_tags(tagstring, image_id):

    #turn 'separated text string' into list
    tags = tagstring.split(";")

    for newimagetag in tags:
        querytag = ImageTag.objects.filter(name = newimagetag)
        if not querytag:
            # ceate one
            currenttag = ImageTag(name = newimagetag)
            currenttag.save()
        else:
            currenttag = querytag[0]
        # add new tag to new image 
        TagMapping.objects.create(albumimage = image_id, imagetag = currenttag)

def _derationalize(rational):
    if type(rational) is rational:
        return rational[0] / rational[1]
    else:
        return 0


def _frombytes(isBytes):
    if type(isBytes) is bytes:
        print ("convert from bytes")
        return isBytes.decode('utf-16').rstrip('\x00')
    else:
        return str(isBytes)

def _create_lookups():

    lookups = {}

    lookups["metering_modes"] = ("Undefined",
                                 "Average",
                                 "Center-weighted average",
                                 "Spot",
                                 "Multi-spot",
                                 "Multi-segment",
                                 "Partial")

    lookups["exposure_programs"] = ("Undefined",
                                    "Manual",
                                    "Program AE",
                                    "Aperture-priority AE",
                                    "Shutter speed priority AE",
                                    "Creative (Slow speed)",
                                    "Action (High speed)",
                                    "Portrait ",
                                    "Landscape",
                                    "Bulb")

    lookups["resolution_units"] = ("",
                                   "Undefined",
                                   "Inches",
                                   "Centimetres")

    lookups["orientations"] = ("",
                               "Horizontal",
                               "Mirror horizontal",
                               "Rotate 180",
                               "Mirror vertical",
                               "Mirror horizontal and rotate 270 CW",
                               "Rotate 90 CW",
                               "Mirror horizontal and rotate 90 CW",
                               "Rotate 270 CW")

    return lookups

def _process_exif_dict(exif_dict):

    date_format = "%Y:%m:%d %H:%M:%S"

    lookups = _create_lookups()

    if "DateTime" in exif_dict.keys():
        exif_dict["DateTime"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTime"]["raw"], date_format)

    if "DateTimeOriginal" in exif_dict.keys():
        exif_dict["DateTimeOriginal"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTimeOriginal"]["raw"], date_format)

    if "DateTimeDigitized" in exif_dict.keys():
        exif_dict["DateTimeDigitized"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTimeDigitized"]["raw"], date_format)

    if "FNumber" in exif_dict.keys():
        exif_dict["FNumber"]["processed"] = \
            _derationalize(exif_dict["FNumber"]["raw"])
        exif_dict["FNumber"]["processed"] = \
            "f{}".format(exif_dict["FNumber"]["processed"])

    if "MaxApertureValue" in exif_dict.keys():
        exif_dict["MaxApertureValue"]["processed"] = \
            _derationalize(exif_dict["MaxApertureValue"]["raw"])
        exif_dict["MaxApertureValue"]["processed"] = \
            "f{:2.1f}".format(exif_dict["MaxApertureValue"]["processed"])

    if "FocalLength" in exif_dict.keys():
        exif_dict["FocalLength"]["processed"] = \
            _derationalize(exif_dict["FocalLength"]["raw"])
        exif_dict["FocalLength"]["processed"] = \
            "{}mm".format(exif_dict["FocalLength"]["processed"])

    if "FocalLengthIn35mmFilm" in exif_dict.keys():
        exif_dict["FocalLengthIn35mmFilm"]["processed"] = \
            "{}mm".format(exif_dict["FocalLengthIn35mmFilm"]["raw"])

    if "Orientation" in exif_dict.keys():
        exif_dict["Orientation"]["processed"] = \
            lookups["orientations"][exif_dict["Orientation"]["raw"]]

#    if "ResolutionUnit" in exif_dict.keys():
#        exif_dict["ResolutionUnit"]["processed"] = \
#            lookups["resolution_units"][exif_dict["ResolutionUnit"]["raw"]]

    if "ExposureProgram" in exif_dict.keys():
        exif_dict["ExposureProgram"]["processed"] = \
            lookups["exposure_programs"][exif_dict["ExposureProgram"]["raw"]]

    if "MeteringMode" in exif_dict.keys():
        exif_dict["MeteringMode"]["processed"] = \
            lookups["metering_modes"][exif_dict["MeteringMode"]["raw"]]

    if "XResolution" in exif_dict.keys():
        exif_dict["XResolution"]["processed"] = \
            int(_derationalize(exif_dict["XResolution"]["raw"]))

    if "YResolution" in exif_dict.keys():
        exif_dict["YResolution"]["processed"] = \
            int(_derationalize(exif_dict["YResolution"]["raw"]))

    if "ExposureTime" in exif_dict.keys():
        exif_dict["ExposureTime"]["processed"] = \
            _derationalize(exif_dict["ExposureTime"]["raw"])
        exif_dict["ExposureTime"]["processed"] = \
            str(Fraction(exif_dict["ExposureTime"]["processed"]).limit_denominator(8000))

    if "ExposureBiasValue" in exif_dict.keys():
        exif_dict["ExposureBiasValue"]["processed"] = \
            _derationalize(exif_dict["ExposureBiasValue"]["raw"])
        exif_dict["ExposureBiasValue"]["processed"] = \
            "{} EV".format(exif_dict["ExposureBiasValue"]["processed"])

    if "XPKeywords" in exif_dict.keys():
        exif_dict["XPKeywords"]["processed"] = \
            _frombytes(exif_dict["XPKeywords"]["raw"])

    if "XPComment" in exif_dict.keys():
        exif_dict["XPComment"]["processed"] = \
            _frombytes(exif_dict["XPComment"]["raw"])

    if "ImageDescription" in exif_dict.keys():
        exif_dict["ImageDescription"]["processed"] = \
            _frombytes(exif_dict["ImageDescription"]["raw"])

    return exif_dict