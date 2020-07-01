
from django.conf.urls import url, include
from django.contrib import admin
from start import views
app_name = 'start'

urlpatterns = [
    url(r'^$',views.index,name='index'),
]
