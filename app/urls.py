from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('url/', views.url_home, name='url_home'),
    path('url/user_urls/', views.user_urls, name='user_urls'),
    path('deactivate/<str:short_url>/', views.deactivate_url, name='deactivate_url'),
]
