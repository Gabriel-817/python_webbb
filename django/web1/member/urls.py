from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name="index"),
    path('join', views.join, name="join"),
    path('list', views.list, name="list"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('edit', views.edit, name="edit"),
    path('delete', views.delete, name="delete"),
    path('join1', views.join1, name="join1"),
]
