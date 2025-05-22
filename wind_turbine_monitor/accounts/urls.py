from django.urls import path
from django.contrib.auth import views as auth_views # Import Django's built-in auth views for password reset/change
from django.contrib.auth.decorators import login_required # Import the login_required decorator
from django.urls import include
from . import views
from django.urls import path, reverse_lazy # Import reverse_lazy for password reset links

urlpatterns = [
    # Include the URLs from the Django authentication system
    path('login/', views.login_view, name='login'),    # Login view
    path('signup/', views.signup_view, name='signup'), # Signup view
    
    # Main dashboard view
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),  # Logout view
    
    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    # Password change views
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),

    # New password change views used admin functionality
    # path(
    #     'password_change/',
    #     auth_views.PasswordChangeView.as_view(
    #         success_url=reverse_lazy('password_change_done')
    #     ),
    #     name='password_change'
    # ),
    
    # path(
    #     'password_change/done/',
    #     auth_views.PasswordChangeDoneView.as_view(
    #         template_name='registration/password_change_done.html'
    #     ),
    #     name='password_change_done'
    # ),

]
