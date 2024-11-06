from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('create/', views.sondage_create, name='sondage_create'),
    path('sondage_list', views.sondage_list, name='sondage_list'),
    path('sondage_delete/<int:sondage_id>/', views.sondage_delete, name='sondage_delete'),
    path('reponse/<int:sondage_id>/', views.reponse, name='reponse'),
    path('analyse/<int:sondage_id>/', views.sondage_analyse, name='sondage_analyse'),
]
