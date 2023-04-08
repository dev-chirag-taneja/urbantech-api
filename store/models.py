from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

from base.models import BaseModel
from accounts.models import User
from .validators import validate_file_size


class Category(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    image = models.ImageField(default='demo.jpg', upload_to='category/', null=True, validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])])

    class Meta: 
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
class Product(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='product')
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.ManyToManyField('ProductSizeVariant', blank=True) 
    color = models.ManyToManyField('ProductColorVariant', blank=True)
    featured_image = models.ImageField(default='demo.jpg', upload_to='products/', null=True, validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])])
    stock = models.IntegerField()
    rating = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    numReviews = models.IntegerField(default=0, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='products/gallery' , validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])])

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'

    def __str__(self):
        return self.product.name
    
    
class ProductSizeVariant(models.Model):
    name = models.CharField(max_length=255, null=True)
    price = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    
class ProductColorVariant(models.Model):
    name = models.CharField(max_length=255, null=True)
    price = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review')
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name}"