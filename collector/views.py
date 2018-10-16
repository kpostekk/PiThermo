import threading
from time import sleep

import w1thermsensor
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse
from gpiozero.output_devices import LED as Relay

from .forms import TempsForm, TimePeriodForm
from .models import Settings, Logs, Temps

# Create your views here.
# Hardware objects
relay = Relay(5)
s = w1thermsensor.W1ThermSensor()


def kget_temp():
    t_high = float(Settings.objects.get(val_key='Temp threshold high').value)
    t_low = float(Settings.objects.get(val_key='Temp threshold low').value)

    t = s.get_temperature()

    if t > t_high and relay.value == True:
        relay.off()
        log = Logs(temp=t, action='0')
        log.save()
    elif t < t_low and relay.value == False:
        relay.on()
        log = Logs(temp=t, action='1')
        log.save()

    lt = Temps(temp=t)
    lt.save()
    # print('lap')

    sleep(50)


def watch_temp():
    while True:
        kget_temp()


th = threading.Thread(target=watch_temp, name='Watchdog')
th.start()


def dashboard_view(request):
    logs = Logs.objects.all().order_by('-timedate')[:150]
    t_high = float(Settings.objects.get(val_key='Temp threshold high').value)
    t_low = float(Settings.objects.get(val_key='Temp threshold low').value)
    return render(request, 'dashboard.html', {'logs': logs, 'temps': {'high': t_high, 'low': t_low}})


def raw_temp(request):
    # temp = randint(2400, 2800) / 100
    temp = s.get_temperature()

    response = HttpResponse(content=temp, content_type='text/plain')
    return response


def set_relay(request, mode):
    if mode:
        relay.on()
        return HttpResponse(content='Relay is on', content_type='text/plain')
    else:
        relay.off()
        return HttpResponse(content='Relay is off', content_type='text/plain')


def get_relay_status(request):
    return HttpResponse(content=relay.value, content_type='text/plain')


def switch_relay(request):
    relay.toggle()
    return HttpResponse(content='Done', content_type='text/plain', status=201)


def settings_view(request):
    if request.method == 'POST':
        form = TempsForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['t_high'] < form.cleaned_data['t_low']:
                return HttpResponse('FORM IS NOT VALID!!!', status=400)
            else:
                st_high = Settings.objects.get(val_key='Temp threshold high')
                st_low = Settings.objects.get(val_key='Temp threshold low')

                st_high.value = form.cleaned_data['t_high']
                st_low.value = form.cleaned_data['t_low']

                st_high.save()
                st_low.save()

                kget_temp()

                return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse('FORM IS NOT VALID!!!', status=400)
    else:
        f = TempsForm(initial={
            't_low': float(Settings.objects.get(val_key='Temp threshold low').value),
            't_high': float(Settings.objects.get(val_key='Temp threshold high').value)
        })
        return render(
            request,
            'settings.html',
            {
                'form': f
            }
        )


def show_period(request):
    if request.method == 'POST':
        form = TimePeriodForm(request.POST)
        if form.is_valid():
            temps = Temps.objects.filter(
                timedate__range=(form.cleaned_data['since'], form.cleaned_data['to'])).order_by('-timedate')
            return render(request, 'history.html', {'form': form, 'temps': temps})
        else:
            return render(request, 'history.html', {'form': form})
    else:
        return render(request, 'history.html', {'form': TimePeriodForm()})
