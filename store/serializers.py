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

    # def get_name(self, obj):
    #     return obj.name

    def create(self, validated_data):
        try:
            return Category.objects.get(name__iexact=validated_data["name"])
        except ObjectDoesNotExist:
            return super(CategorySerializer, self).create(validated_data)


# Product Size Serializer
class ProductSizeVariantSerializer(serializers.ModelSerializer):
    # size = serializers.SerializerMethodField()

    class Meta:
        model = ProductSizeVariant
        fields = ["name"]

    # def get_size(self, obj):
    #     return [size.name for size in obj.size.all()]

    def create(self, validated_data):
        try:
            return ProductSizeVariant.objects.get(name__iexact=validated_data["name"])
        except ObjectDoesNotExist:
            return super(ProductSizeVariantSerializer, self).create(validated_data)


# Product Color Serializer
class ProductColorVariantSerializer(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField()

    class Meta:
        model = ProductColorVariant
        fields = ["name"]

    # def get_name(self, obj):
    #     return [color.name for color in obj.name]

    def create(self, validated_data):
        try:
            return ProductColorVariant.objects.get(name__iexact=validated_data["name"])
        except ObjectDoesNotExist:
            return super(ProductColorVariantSerializer, self).create(validated_data)


# Product Gallery Serializer
class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ["id", "image"]

    def create(self, validated_data):
        slug = self.context["slug"]
        product = Product.objects.get(slug=slug)
        return ProductGallery.objects.create(product=product, **validated_data)


# Product Serializer
class ProductSerializer(WritableNestedModelSerializer):
    category = CategorySerializer(many=False)
    # category = serializers.CharField(max_length=255)
    size = ProductSizeVariantSerializer(many=True)
    color = ProductColorVariantSerializer(many=True)
    slug = serializers.StringRelatedField(read_only=True)
    images = serializers.SerializerMethodField()
    # images = ProductGallerySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "slug",
            "name",
            "description",
            "price",
            "size",
            "color",
            "featured_image",
            "stock",
            "images",
            "rating",
            "numReviews",
        ]
        
    def get_images(self, obj):
        return [image.image.url for image in obj.images.all()]


# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ["id", "user", "name", "description", "created_at"]

    def create(self, validated_data):
        user = self.context["user"]
        slug = self.context["slug"]
        product = Product.objects.get(slug=slug)
        return Review.objects.create(user=user, product=product, **validated_data)

    def update(self, instance, validated_data):
        user = self.context["user"]
        if user.is_staff or instance.user == user:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                {"message": "You don't have permission to perform this action."}
            )
