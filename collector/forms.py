from django.forms import Form, FloatField, NumberInput, DateTimeField, DateTimeInput


class TempsForm(Form):
    t_high = FloatField(widget=NumberInput(attrs={'class': 'form-control'}))
    t_low = FloatField(widget=NumberInput(attrs={'class': 'form-control'}))
    t_high.label = 'Temperatura wyłączania przekaźnika'
    t_low.label = 'Temperatura włączania przekaźnika'


class TimePeriodForm(Form):
    since = DateTimeField(widget=DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}))
    to = DateTimeField(widget=DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}))
    since.label = 'Od'
    to.label = 'Do'
