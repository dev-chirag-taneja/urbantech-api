from django.contrib import admin
import admin_thumbnails

from .models import *


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": [
            "name",
        ]
    }
    list_display = ["name", "slug"]


@admin_thumbnails.thumbnail("image")
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 3


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": [
            "name",
        ]
    }
    list_display = [
        "name",
        "price",
        "stock",
        "category",
        "featured_image",
        "updated_at",
    ]
    search_fields = ["name"]
    list_filter = ["category"]
    list_per_page = 50
    inlines = [ProductGalleryInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductGallery)
admin.site.register(ProductSizeVariant)
admin.site.register(ProductColorVariant)
admin.site.register(Review)
