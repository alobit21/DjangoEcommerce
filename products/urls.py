
from django.urls import path

from . import views
urlpatterns = [
    path('shop/<slug:slug>', views.product, name="product"),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
]
