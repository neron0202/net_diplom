from django.contrib import admin
from django.urls import path

from orbackend.views import GoodsUpload

urlpatterns = [
    path('admin/', admin.site.urls),
    path('partner/', GoodsUpload.as_view())
]
