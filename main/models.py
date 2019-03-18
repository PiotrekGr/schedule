from django.db import models
from django.contrib.auth.models import User

# Create your models here.

COLORS = (          # todo przygotować paletę kolorów https://farbelous.io/bootstrap-colorpicker/
    (1, 'blue'),
    (2, 'green'),
    (3, 'red'),
    (4, 'yellow'),
    (5, 'violet'),
)


class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Activities(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    priority = models.IntegerField()
    assumed_time = models.FloatField()
    applied_time = models.FloatField()
    color = models.IntegerField(choices=COLORS) # todo nadpisać str, żeby wyświetłały się nazwy kolorów


class Availability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_time = models.DateTimeField() # todo ograniczenie co pół godziny
    end_time = models.DateTimeField() # todo ograniczenie co pół godziny
    duration = models.FloatField() # todo oblieczenia w poście?, wartości zaokrąglone do połówek


class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    slot = models.ForeignKey(Availability, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE)
    order = models.IntegerField()
    duration = models.FloatField() # todo wartości zaokrąglone do połówek
    execution = models.FloatField(null=True)
