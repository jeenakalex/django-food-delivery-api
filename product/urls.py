from django.urls import path
from product.views import ProductCreateView, ProductListView, ProductRetrieveUpdateDeleteView, UploadProductsView, UploadProgressView


urlpatterns = [

    path('create/', ProductCreateView.as_view(), name='product-list-create'),
    path('list/', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductRetrieveUpdateDeleteView.as_view(), name='product-detail'),
    path('upload/', UploadProductsView.as_view(), name='upload-products'),
    path('upload-progress/<str:upload_id>/', UploadProgressView.as_view(), name='upload-progress'),
    
]