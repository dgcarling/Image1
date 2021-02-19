# accounts/urls.py
from django.urls import path

import gallery.forms
import gallery.views

urlpatterns = [
    path('new/', gallery.views.AlbumCreateView.as_view(), name = 'album_new'),
    path('<slug:slug>/', gallery.views.AlbumDetail.as_view(), name='album'),
    path('', gallery.views.gallery, name='gallery'),
]

handler404 = 'gallery.views.handler404'