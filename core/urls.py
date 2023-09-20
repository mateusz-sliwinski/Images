# Django
from django.urls import path

from core.views import UploadImageView, ListImagesView
# Project
from project import settings

urlpatterns = [
    path('upload_image/', UploadImageView.as_view(), name='upload_image'),
    path('list_images/', ListImagesView.as_view(), name='list_images'),
]
