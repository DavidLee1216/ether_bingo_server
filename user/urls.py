from . import views
from django.urls import path

urlpatterns = [
    path('signup/', views.signup, name='sign-up'),
    path('signin/', views.signin, name='sign-in'),
    path('signout/', views.signout, name='sign-out'),
    path('auth/', views.authorize, name='authorize'),
    path('resend_mail/', views.resend_auth_email, name='resend-email'),

    path('auth/<int:id>/verify/<str:key>',
         views.email_authorize, name='email-auth'),
    # path('resetpass/', views.reset_password, name='reset-pass'),
]
