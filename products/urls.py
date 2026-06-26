from django.urls import path
from .views import ProductSearchView, ProductDetailView, ProductByCategoryView, ProductCreateView

urlpatterns = [
    path('search', ProductSearchView.as_view(), name='product-search'),
    path('<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('category/<str:category>', ProductByCategoryView.as_view(), name='products-by-category'),
    path('', ProductCreateView.as_view(), name='product-create'),
]
