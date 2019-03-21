from django import forms

from main.models import COLORS, TIME


class AddPlan(forms.Form):
    starting_date = forms.DateField(widget=forms.SelectDateWidget, label='first day of weekly plan') # todo set current date, add weekday


class AddActivity(forms.Form):
    name = forms.CharField(max_length=10)
    description = forms.CharField(max_length=255)
    priority = forms.IntegerField(max_value=10, min_value=1)
    assumed_time = forms.FloatField(min_value=0, max_value=15)
    color = forms.ChoiceField(choices=COLORS)


class AddAvailability(forms.Form):
    day = forms.IntegerField(min_value=1, max_value=7)
    start_time = forms.ChoiceField(choices=TIME)
    end_time = forms.ChoiceField(choices=TIME)
