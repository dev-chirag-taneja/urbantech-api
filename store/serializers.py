from requests import request
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token
from drf_writable_nested.serializers import WritableNestedModelSerializer
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from store.models import *


# Category Serializer     
class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    
    class Meta:
        model = Category
        fields = ["name"]
        
    def create(self, validated_data):
        try:
            return Category.objects.get(name__iexact = validated_data['name'])
        except ObjectDoesNotExist: 
            return super(CategorySerializer, self).create(validated_data)


# Product Size Serializer     
class ProductSizeVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSizeVariant
        fields = ["name"]
        
    def create(self, validated_data):
        try:
            return ProductSizeVariant.objects.get(name__iexact = validated_data['name'])
        except ObjectDoesNotExist: 
            return super(ProductSizeVariantSerializer, self).create(validated_data)


# Product Color Serializer     
class ProductColorVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColorVariant
        fields = ["name"]
        
    def create(self, validated_data):
        try:
            return ProductColorVariant.objects.get(name__iexact = validated_data['name'])
        except ObjectDoesNotExist: 
            return super(ProductColorVariantSerializer, self).create(validated_data)


# Product Gallery Serializer     
class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ["id", "image"]    
        
    def create(self, validated_data):
        slug = self.context['slug']
        product = Product.objects.get(slug=slug)
        return ProductGallery.objects.create(product=product, **validated_data)
   

# Product Serializer     
class ProductSerializer(WritableNestedModelSerializer):
    category = CategorySerializer(many=False)
    size = ProductSizeVariantSerializer(many=True)
    color = ProductColorVariantSerializer(many=True)
    images = ProductGallerySerializer(many=True, read_only=True)
    slug = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Product
        fields = ["id", "category", "slug", "name", "description", "price", "size", "color", "featured_image", "stock", "images", "rating", "numReviews"]


# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Review
        fields = ["id", "user", "name", "description", "created_at"]

    def create(self, validated_data):
        user = self.context['user']
        slug = self.context['slug']
        product = Product.objects.get(slug=slug)
        return Review.objects.create(user=user, product=product, **validated_data)


# Review Serializer
class ReviewDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Review
        fields = ["id", "user", "name", "description", "created_at"]
        
    def validate(self, obj):
        user = self.context['user']
        if user.is_admin:
            return obj
        try:
            Review.objects.get(id=self.context['pk'], user=user)
        except:
            raise ValidationError({"message":"You dont have permission to perform this action!"})
        return obj