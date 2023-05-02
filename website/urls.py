from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('meeting_rooms/', views.meeting_rooms, name='meeting_rooms'),
    path('meeting_rooms/add_mr', views.add_mr, name='add_mr'),
    path('meeting_rooms/update_mr/<int:pk>', views.update_mr, name='update_mr'),
    path('meeting_rooms/<int:pk>/history/', views.history, name='history'),
    path('meeting_rooms/<int:pk>/add_history/', views.add_history, name='add_history'),
    path('meeting_rooms/<int:pk1>/update_history/<int:pk2>', views.update_history, name='update_history'),
    path('admin_list/', views.admin_list, name='admin_list'),
    path('add_admin', views.add_admin, name='add_admin'),
    # path('register/', views.register_user, name='register'),
    # path('delete_record/<int:pk>', views.delete_record, name='delete_record'),

]