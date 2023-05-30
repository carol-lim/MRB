from django.urls import path
from . import views
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('search/', views.search, name='search'),
    path('booking/', views.booking, name='booking'),
    path('meeting_rooms/', views.meeting_rooms, name='meeting_rooms'),
    path('meeting_rooms/add_mr/', views.add_mr, name='add_mr'),
    path('meeting_rooms/update_mr/<int:pk>', views.update_mr, name='update_mr'),
    path('meeting_rooms/<int:pk>/history/', views.history, name='history'),
    path('meeting_rooms/<int:pk>/add_history/', views.add_history, name='add_history'),
    path('meeting_rooms/<int:pk1>/update_history/<int:pk2>/', views.update_history, name='update_history'),
    path('available_now/', views.available_now, name='available_now'),
    path('scheduled/', views.scheduled, name='scheduled'),
    path('now_in_use/', views.now_in_use, name='now_in_use'),
    path('admin_list/', views.admin_list, name='admin_list'),
    path('add_admin/', views.add_admin, name='add_admin'),
    path('set_password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='set_password.html'), name='set_password'),

    # path("password_reset/", auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path("password_reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name='set_password_complete.html'), name='password_reset_complete'),

    # path('set_password/<str:uidb64>/<str:token>/', views.set_password, name='set_password'),
    # path('register/', views.register_user, name='register'),
    # path('delete_record/<int:pk>', views.delete_record, name='delete_record'),

]