from django.urls import path

from .views import hello

urlpatterns = [
    path('b/', hello, name='test'),

]
