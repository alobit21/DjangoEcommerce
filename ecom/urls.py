from django.conf import settings
from django.conf.urls.static import static
from cart.views import add_to_cart
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('logout/', views.LogoutView.as_view(), name='logout'),  # Use built-in LogoutView
    path('product/', include('products.urls')),
    path('cart/', include('cart.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
