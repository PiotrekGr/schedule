import datetime

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

COLORS = (          # todo przygotować paletę kolorów https://farbelous.io/bootstrap-colorpicker/
    (1, 'CadetBlue'),
    (2, 'Coral'),
    (3, 'CornFlowerBlue'),
    (4, 'Crimson'),
    (5, 'PaleVioletRed'),
    (6, 'LightBlue'),
    (7, 'DarkKhaki'),
    (8, 'DarkGoldenRod'),
    (9, 'LightSeaGreen'),
    (10, 'Olive'),
)


# TIME = [(i, datetime.timedelta(minutes=i*30)) for i in range(48)]
TIME = [(i, datetime.timedelta(minutes=i*30)) for i in range(14,45)]


class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('start_date', 'created', )


class Activities(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    priority = models.IntegerField()
    assumed_time = models.FloatField()
    applied_time = models.FloatField(default=0)
    color = models.IntegerField(choices=COLORS) # todo nadpisać str, żeby wyświetłały się nazwy kolorów

    class Meta:
        ordering = ('plan_id', '-priority', )


class Availability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    day = models.IntegerField(default=1)
    start_time = models.IntegerField(choices=TIME) # todo ograniczenie co pół godziny
    end_time = models.IntegerField(choices=TIME) # todo ograniczenie co pół godziny
    duration = models.FloatField() # todo obliczenia w poście?, wartości zaokrąglone do połówek

    class Meta:
        ordering = ('plan_id', 'day','start_time', )


class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    slot = models.ForeignKey(Availability, on_delete=models.CASCADE)
    start_time = models.IntegerField(choices=TIME)
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE)
    order = models.IntegerField()
    duration = models.FloatField() # todo wartości zaokrąglone do połówek
    execution = models.FloatField(null=True)
