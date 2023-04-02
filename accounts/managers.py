from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def create_user(self, first_name, last_name, email, password=None,  **extra_fields):
        if not email:
            raise ValueError('User must have an email address.')

        user = self.model(
            first_name = first_name,
            last_name = last_name,
            email = self.normalize_email(email),
            )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, password=None,  **extra_fields):
        user = self.create_user(
        first_name = first_name,
        last_name = last_name,
        email = self.normalize_email(email),
        password = password)

        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user