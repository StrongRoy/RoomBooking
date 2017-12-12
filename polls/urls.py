
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index),
    url(r'^index/$', views.index,name='index'),
    url(r'^users/login/$',views.login,name='login'),
    url(r'^users/logout/$',views.logout,name='logout'),
    url(r'^booking/info/$',views.get_booking_info,name='booking_info'),

]
