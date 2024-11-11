from django.urls import path
from . import views

urlpatterns = [
    # path('', views.web),
    path('hello/', views.hello_world),
    path('', views.index),
    path('ajax_data/', views.ajax_data),
]