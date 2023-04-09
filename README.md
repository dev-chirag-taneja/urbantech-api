<h1>Emart API</h1>

[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-4.1.7-darkgreen.svg)](https://djangoproject.com)

<p>
Emart is an ecommerce application built on Django Framework and has all the required features that an ecommerce type application need.
Some of the projects features are mentioned below.
</p>

## Features
```
- Account/Auth API
- Store API
- Cart API
- Order API
- Payment API
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

## Installation
```
# Clone the Repo
- git clone https://github.com/dev-chirag-taneja/django-emart-api.git

# Go to directory
- cd django-emart-api

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