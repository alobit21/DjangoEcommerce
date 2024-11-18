from django.urls import path
from core import views  # Import your own views
from django.contrib.auth import views as auth_views  # Rename import to avoid conflict

urlpatterns = [
    path('', views.frontpage, name="frontpage"),
    path('shop/', views.shop, name="shop"),
    path('signup/', views.signup, name="signup"),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name="login"),  # Use the renamed import
    path('logout/', views.user_logout, name='user_logout'),  # Use custom logout view
]
