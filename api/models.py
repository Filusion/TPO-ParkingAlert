from django.db import models
from django.utils import timezone

# Create your models here.

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.TextField()

    def __str__(self):
        return self.url
    
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="users"
    )

    image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    def __str__(self):
        return self.username

class UserData(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="users_data"
    )
    ts_ins = models.DateTimeField(default=timezone.now,
        null=True,
        blank=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.user

class SlovenskeUlice(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class SlovenskaMesta(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class ParkirnaMesta(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    def __str__(self):
        return self.name