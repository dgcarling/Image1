#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from django import forms
from gallery.models import Album, AlbumImage, ImageTag, TagMapping

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        exclude = []

    zip = forms.FileField(required=False)

class AlbumCreateForm(forms.ModelForm):
    class Meta:
        model = Album
        exclude = []

    zip = forms.FileField(required=False)    

class AlbumImageForm(forms.ModelForm):
    class Meta:
        model = AlbumImage
        exclude = []    

class ImageTagForm(forms.ModelForm):
    class Meta:
        model = ImageTag
        exclude = []   

class TagMappingForm(forms.ModelForm):
    class Meta:
        model = TagMapping
        exclude = []   