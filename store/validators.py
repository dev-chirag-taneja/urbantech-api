from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_size_mb = 2000 * 1000

    if file.size > max_size_mb:
        raise ValidationError(f"File size cannot be larger than 2 mb.")
