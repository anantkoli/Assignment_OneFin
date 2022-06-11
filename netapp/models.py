from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    password =  models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class Collections(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Movies(models.Model):
    cid  = models.BigIntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    genres = models.CharField(max_length=255)
    uuid = models.CharField(max_length=255)

class Counts(models.Model):
    val = models.IntegerField(default=0)