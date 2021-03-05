from django.urls import path

from .views import error, good

urlpatterns = [
    path('error/', error, name='error'),
    path('good/', good, name='good'),
]
