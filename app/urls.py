from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('url/', views.url_home, name='url_home'),
    path('url/user_urls/', views.user_urls, name='user_urls'),
    path('url/deactivate/<str:short_url>/', views.deactivate_url, name='deactivate_url'),
    path('url/activate/<str:short_url>/', views.activate_url, name='activate_url'),
    path('url/delete/<str:short_url>/', views.delete_url, name='delete_url'),
    path('url/validity_period/<str:short_url>/', views.update_validity_period, name='update_validity_period'),

    path('qrcode/', views.qrcode_home, name='qrcode_home'),

    path('imagetopdf/', views.imagetopdf_home, name='imagetopdf_home'),

    path('quicknote/', views.quicknote_home, name='quicknote_home'),
    path('quicknote/user-list/', views.get_user_from_api, name='user_list'),
    path('quicknote/sent-notes/', views.sent_notes_view, name='sent_notes'),
    path('quicknote/received-notes/', views.received_notes_view, name='received_notes'),
    path('quicknote/received-notes/<int:note_id>/', views.received_note_detail_view, name='received_notes_detail'),
    path('quicknote/sent-notes/<int:note_id>/', views.sent_note_detail_view, name='sent_notes_detail'),
]
