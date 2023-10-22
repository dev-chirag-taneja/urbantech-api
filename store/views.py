from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics 
from rest_framework import parsers
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404

import json

from .serializers import *
from .permissions import IsAdminOrReadOnly
from .paginations import CustomPagePagination
from .filters import ProductFilter


# Category Api
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CustomPagePagination


# Product List Api
class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CustomPagePagination
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['slug', 'description', 'category__slug']
    ordering_fields = ['price', 'updated_at']
    
    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('color', 'size', 'images')

    def post(self, request):
        try:
            featured_image = request.data['featured_image']
        except: 
            featured_image = None
            
        data = json.loads(request.data['data'])
        data['featured_image'] = featured_image
        serializer = ProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
   
    
# Product Detail Api
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(slug=self.kwargs['slug'])
    
    def put(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        try:
            featured_image = request.data['featured_image']
        except: 
            featured_image = None
            
        data = json.loads(request.data['data'])
        data['featured_image'] = featured_image
        serializer = ProductSerializer(product, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)   


# Product Image List Api
class ProductImageListView(generics.ListCreateAPIView):
    serializer_class = ProductGallerySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
        
    def get_queryset(self):
        return ProductGallery.objects.filter(product__slug=self.kwargs['slug'])
    
    def get_serializer_context(self):
        return {'slug' : self.kwargs['slug']}
          
        
# Product Image Detail Api
class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductGallerySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return ProductGallery.objects.filter(id=self.kwargs['pk'])
    
    
# Product Review List Api
class ReviewListView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Review.objects.filter(product__slug=self.kwargs['slug'])

    def get_serializer_context(self):
        return {'user': self.request.user, 'slug': self.kwargs['slug']}
    
    
# Product Review Detail Api
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Review.objects.filter(id=self.kwargs['pk'])

    def get_serializer_context(self):
        return {'user': self.request.user, 'pk': self.kwargs['pk']}
    
    def destroy(self, request, *args, **kwargs):
        try:
            review = Review.objects.get(id=self.kwargs['pk'])
            if request.user.is_admin or review.user == request.user:
                review.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(data={"message": "You dont have permission to perform this action!"}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(data={"message": "Review not found!"}, status=status.HTTP_400_BAD_REQUEST)