<h1>UrbanTech API</h1>

[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-4.1.7-darkgreen.svg)](https://djangoproject.com)

<p>
UrbanTech is an ecommerce application built on Django Framework and has all the required features that an ecommerce type application need.
Some of the projects features are mentioned below.
</p>

## Features
```
- Auth API :
Login, Register, Activate User, Password Change, User Profile

- Store API :
Categories, Products, Images, Reviews

- Cart API :
Cart, Add to Cart, Delete and Remove from Cart

- Order API : 
Checkout, Payment, Orders
``` 

## Tech Stack
```
# Backend    
- Python, Django

# Database   
- Sqlite

# API   
- Django Rest Framework
```

## Technical Information
```
Some Django and Rest Framework Features Used In Project : 

- Django Signals
- Django Email
- Product OrderingFilter, SearchFilter
- File Size Validation
- Custom Pagination and Permissions
```

## Installation
```
# Clone the Repo
- git clone https://github.com/dev-chirag-taneja/urbantech-api.git

# Go to directory
- cd urbantech-api

# Create a virtual environment
- python -m virtualenv env

# Activate the virtual environment
- source env/bin/activate

# Install the required dependency
- pip install -r requirements.txt

# Configure .env
- Rename env.example file to .env
- Put your credentials.

SECRET_KEY=
DEBUG=
EMAIL_HOST=
EMAIL_USE_TLS=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Make migrations
- python manage.py migrate

# Create superuser
- python manage.py createsuperuser

# Run the server
- python manage.py runserver
```

<p align="center">Made with ❤️ and Python</p>