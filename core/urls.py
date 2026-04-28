from django.urls import path
from core import views  # Import your own views
from django.contrib.auth import views as auth_views  # Rename import to avoid conflict

urlpatterns = [
    
    path('', views.frontpage, name="home"),
    path('frontpage/', views.frontpage, name="frontpage"),
    path('shop/', views.shop, name="shop"),
    path('products/', views.shop, name="product_list"),
    path('search/', views.shop, name="product_search"),
    path('signup/', views.signup, name="signup"),
    path('register/', views.signup, name="register"),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name="login"),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name="profile"),
    path('profile/update/', views.profile_update, name="profile_update"),
    path('profile/change-password/', auth_views.PasswordChangeView.as_view(template_name='core/change_password.html', success_url='/profile/'), name='change_password'),
    path('orders/', views.order_history, name="order_history"),
    path('orders/<int:order_id>/', views.order_detail, name="order_detail"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('categories/', views.category_list, name="category_list"),
]
