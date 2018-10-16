from django.db import models


# Create your models here.


class Settings(models.Model):
    val_key = models.CharField(max_length=128, unique=True)
    value = models.CharField(max_length=4096, null=True)


class Logs(models.Model):
    temp = models.FloatField()
    timedate = models.DateTimeField(auto_now_add=True)
    action = models.CharField(choices=(('0', 'Wyłączono grzejnik'), ('1', 'Włączono grzejnik')), max_length=1)

    class Meta:
        ordering = ['-timedate']


class Temps(models.Model):
    temp = models.FloatField()
    timedate = models.DateTimeField(auto_now_add=True)
