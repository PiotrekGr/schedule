import datetime

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


TIME = [(i, datetime.timedelta(minutes=i*30)) for i in range(48)]

# TIME = (
#     (0, datetime.time(hour=0, minute=0)),
#     (0.5, '00:30'),
#     (1, '01:00'),
#     (1.5, '01:30'),
#     (2, '02:00'),
#     (2., '02:30'),
#     (3, '03:00'),
#     (3.5, '03:30'),
#     (4, '04:00'),
#     (4.5, '04:30'),
#     (5, '05:00'),
#     (5.5, '05:30'),
#     (6, '06:00'),
#     (6.5, '06:30'),
#     (7, '07:00'),
#     (7.5, '07:30'),
#     (8, '08:00'),
#     (8.5, '08:30'),
#     (9, '09:00'),
#     (9.5, '09:30'),
#     (10, '10:00'),
#     (10., '10:30'),
#     (11, '11:00'),
#     (11.5, '11:30'),
#     (12, '12:00'),
#     (12.5, '12:30'),
#     (13, '13:00'),
#     (13.5, '13:30'),
#     (14, '14:00'),
#     (14.5, '14:30'),
#     (15, '15:00'),
#     (15.5, '15:30'),
#     (16, '16:00'),
#     (16.5, '16:30'),
#     (17, '17:00'),
#     (17.5, '17:30'),
#     (18, '18:00'),
#     (18.5, '18:30'),
#     (19, '19:00'),
#     (19.5, '19:30'),
#     (20, '20:00'),
#     (20.5, '20:30'),
#     (21, '21:00'),
#     (21.5, '21:30'),
#     (22, '22:00'),
#     (22.5, '22:30'),
#     (23, '23:00'),
#     (23.5, '23:30'),
#     (24, '24:00')
# )




class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


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
