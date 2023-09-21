# Django
from django.urls import path

# Project
from core.views import ListImagesView
from core.views import TokenView
from core.views import UploadImageView

urlpatterns = [
    path('upload_image/', UploadImageView.as_view(), name='upload_image'),
    path('list_images/', ListImagesView.as_view(), name='list_images'),
    path('token/<str:token>/', TokenView.as_view(), name='token_view'),

]
