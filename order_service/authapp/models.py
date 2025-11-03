from django.db import models


class User(models.Model):
    IdUser = models.AutoField(primary_key=True)
    UserName = models.CharField(max_length=255, unique=True)
    Password = models.CharField(max_length=255)
    Token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.UserName

