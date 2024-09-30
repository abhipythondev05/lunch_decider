from django.contrib.auth.models import AbstractUser
from django.db import models


class Employee(AbstractUser):
    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"


class Restaurant(models.Model):
    name = models.CharField(max_length=100)


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date = models.DateField()
    items = models.JSONField()  # List of items as text or JSON


class Vote(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    points = models.IntegerField()  # 1 for older version, 1 to 3 for newer version
