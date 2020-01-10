# 파일명 : api/urls.py - 직접 생성
from django.urls import path
from . import views

urlpatterns = [
    path('insert1', views.insert1, name="insert1"),
    path('select1', views.select1, name="select1"),
    path('select2', views.select2, name="select2"),
    path('select_ex', views.select_ex, name="select_ex"),
]
