from django.urls import path
from . import views
import MeetingRoom.views as MRViews
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('home/', MRViews.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('signup_admin/<str:uuid>', views.signup_admin, name='signup_admin'),
    path('admin_list/', views.admin_list, name='admin_list'),
    path('add_admin/', views.add_admin, name='add_admin'),
    path("admin_list/deleteInvitation/<str:pk>",views.deleteInvitation, name="deleteInvitation"),
    path('set_password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='set_password.html'), name='set_password'),

    # path("password_reset/", auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path("password_reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name='set_password_complete.html'), name='password_reset_complete'),

    # path('set_password/<str:uidb64>/<str:token>/', views.set_password, name='set_password'),
    # path('register/', views.register_user, name='register'),
    # path('delete_record/<int:pk>', views.delete_record, name='delete_record'),

]