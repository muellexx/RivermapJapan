from django.contrib.auth import views as auth_views
from django.urls import path
from . import views as user_views
from .views import ProfileView


urlpatterns = [
    path('register/', user_views.register, name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', user_views.profile_edit, name='profile-edit'),
    path('profile/delete/', user_views.profile_delete, name='profile-delete'),
    path('profile/delete/done/', user_views.profile_delete_done, name='profile-delete-done'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('activate/<slug:uidb64>/<slug:token>/', user_views.activate,  name='activate')
]