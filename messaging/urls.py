from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.create_message, name='create_message'),
    path('messages/mark-read/', views.mark_message_read, name='mark_message_read'),
    path('messages/list/', views.list_messages, name='list_messages'),
]
