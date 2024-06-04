from django.core.cache import cache
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


# Category List View
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CustomPagePagination

    def list(self, request, *args, **kwargs):
        cache_key = "category_list"  # Define the cache key
        cached_categories = cache.get(
            cache_key
        )  # Try to get the category data from the cache

        # If cached data is found, return it directly
        if cached_categories:
            return Response({"name": cached_categories})

        queryset = self.get_queryset()

        # Check if pagination is required
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            category_names = [category["name"] for category in serializer.data]
            # Cache the serialized data for 1 hour (3600 seconds)
            cache.set(cache_key, category_names, timeout=60 * 60)
            return self.get_paginated_response({"name": category_names})

        serializer = self.get_serializer(queryset, many=True)
        category_names = [category["name"] for category in serializer.data]
        cache.set(cache_key, category_names, timeout=60 * 60)
        return Response({"name": category_names})


# Product List View
class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CustomPagePagination
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["slug", "description", "category__slug"]
    ordering_fields = ["price", "updated_at"]

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "color", "size", "images"
        )

    def create(self, request):
        try:
            featured_image = request.data["featured_image"]
        except:
            featured_image = None

        data = json.loads(request.data["data"])
        data["featured_image"] = featured_image

        print(data)

        # Fetch category object by name
        category_name = data.pop("category", None)
        if category_name:
            category, _ = Category.objects.get_or_create(name__iexact=category_name)
            data["category"] = category

        # Fetch or create size objects by name
        size_names = data.pop("size", [])
        size_ids = []
        for name in size_names:
            size, _ = ProductSizeVariant.objects.get_or_create(name__iexact=name)
            size_ids.append(size.id)
        data["size"] = size_ids

        # Fetch or create color objects by name
        color_names = data.pop("color", [])
        color_ids = []
        for name in color_names:
            color, _ = ProductColorVariant.objects.get_or_create(name__iexact=name)
            color_ids.append(color.id)
        data["color"] = color_ids

        print(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Product Detail View
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.filter(slug=self.kwargs["slug"])

    def put(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        try:
            featured_image = request.data["featured_image"]
        except:
            featured_image = None

        data = json.loads(request.data["data"])
        data["featured_image"] = featured_image
        serializer = ProductSerializer(product, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Product Image List View
class ProductImageListView(generics.ListCreateAPIView):
    serializer_class = ProductGallerySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        return ProductGallery.objects.filter(product__slug=self.kwargs["slug"])

    def get_serializer_context(self):
        return {"slug": self.kwargs["slug"]}


# Product Image Detail View
class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductGallerySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return ProductGallery.objects.filter(id=self.kwargs["pk"])


# Product Review List View
class ReviewListView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    cache_timeout = 120
    
    def get_cache_key(self):
        return f"review_list_{self.kwargs['slug']}"

    def get_queryset(self):
        cache_key = self.get_cache_key()
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = Review.objects.filter(product__slug=self.kwargs["slug"]).prefetch_related("user")
            cache.set(cache_key, queryset, timeout=self.cache_timeout)
        return queryset


    def get_serializer_context(self):
        return {"user": self.request.user, "slug": self.kwargs["slug"]}


# Product Review Detail View
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(id=self.kwargs["pk"])

    def get_serializer_context(self):
        return {"user": self.request.user, "pk": self.kwargs["pk"]}

    def destroy(self, request, *args, **kwargs):
        try:
            review = Review.objects.get(id=self.kwargs["pk"])
            if request.user.is_admin or review.user == request.user:
                review.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    data={
                        "message": "You dont have permission to perform this action!"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ObjectDoesNotExist:
            return Response(
                data={"message": "Review not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
