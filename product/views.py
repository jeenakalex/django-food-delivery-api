import django_filters
import csv
import os

from django.conf import settings
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from django.core.files.storage import default_storage

from .models import Product
from .serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from user.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .tasks import process_csv_upload
from celery.result import AsyncResult
from django.http import JsonResponse


class ProductCreateView(generics.ListCreateAPIView):
    """Create and list all products"""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def create(self, request, *args, **kwargs):
        """create product"""
        response = super().create(request, *args, **kwargs)
        return Response({"message": "Product created successfully!", "data": response.data}, status=status.HTTP_201_CREATED)


class ProductFilter(django_filters.FilterSet):
    """Class to get product list based on filter"""
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ['status', 'min_price', 'max_price', 'name']


class ProductListView(generics.ListAPIView):
    """List products based on filters"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

class ProductRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve and delete products"""
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)  # Allow image upload
    
    def update(self, request, *args, **kwargs):
        """Update product and return response"""
        response = super().update(request, *args, **kwargs)
        return Response({"message": "Product updated successfully!", "data": response.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Delete product and return response"""
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Product deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)



## Bulk Upload
class UploadProductsView(APIView):
    """ API to upload products CSV file """
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({"error": "No file uploaded"}, status=400)

        # Ensure uploads folder exists
        upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Define the file path
        file_path = os.path.join(upload_dir, uploaded_file.name)

        # Save file to disk
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        task = process_csv_upload.delay(file_path)
        return Response({"message": "File uploaded successfully", "upload_id": task.id}, status=status.HTTP_200_OK)

class UploadProgressView(APIView):
    """ API to check upload progress """

    def get(self, request, upload_id):
        
        task = AsyncResult(upload_id)

        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'progress': 0
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'progress': task.info.get('progress', 0)
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'progress': 100
            }
        else:
            response = {
                'state': task.state,
                'progress': 0,
                'error': str(task.info)
            }

        return JsonResponse(response)