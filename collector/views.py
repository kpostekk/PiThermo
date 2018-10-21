import datetime
import logging
import threading
from time import sleep

import w1thermsensor
import yaml
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse
from gpiozero.output_devices import LED as Relay

from .forms import TempsForm, TimePeriodForm
from .models import Settings, Logs, Temps

# Hardware objects
relay = Relay(5)
s = w1thermsensor.W1ThermSensor()

# Config objects
logging.addLevelName(240, "TEMPSLOG")
logging.basicConfig(filename='temps.csv',
                    format='%(mytime)s;%(message)s;%(temp)s;%(relay_mode)s;%(th_high)s;%(th_low)s', level=240)
# logging.log(level=240, msg='Config message', extra={'mytime': 'Date', 'temp': 'Temp.', 'relay_mode': 'Relay', 'th_high': 'High', 'th_low': 'Low'})
config_file = open('./PieTemp/config.yaml', mode='r')
config_yaml = yaml.load(config_file)
wt_delay = config_yaml['temp_checker']


# Defining utils and watchdogs
def update_config():
    global config_file
    global config_yaml
    config_file = open('./PieTemp/config.yaml', mode='w+')
    config_file.write(yaml.dump(config_yaml, indent=4, default_flow_style=False))
    config_file = open('./PieTemp/config.yaml', mode='r')


def kget_temp():
    t_high = float(config_yaml['treshold_high'])
    t_low = float(config_yaml['treshold_low'])

    t = s.get_temperature()

    if t > t_high and relay.value == True:
        relay.off()
        log = Logs(temp=t, action='0')
        log.save()
    elif t < t_low and relay.value == False:
        relay.on()
        log = Logs(temp=t, action='1')
        log.save()

    logging.log(level=240, msg='Collected temperature',
                extra={
                    'mytime': datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'),
                    'temp': t,
                    'relay_mode': relay.value,
                    'th_high': t_high,
                    'th_low': t_low
                })


def watch_temp():
    while True:
        kget_temp()
        sleep(wt_delay)


# Starting watchdogs
th = threading.Thread(target=watch_temp, name='Watchdog')
th.start()


# Rest of views are here
def dashboard_view(request):
    logs = Logs.objects.all().order_by('-timedate')[:150]
    t_high = float(config_yaml['treshold_high'])
    t_low = float(config_yaml['treshold_low'])
    return render(request, 'dashboard.html', {'logs': logs, 'temps': {'high': t_high, 'low': t_low}})


def raw_temp(request):
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
                config_yaml['treshold_high'] = form.cleaned_data['t_high']
                config_yaml['treshold_low'] = form.cleaned_data['t_low']

                update_config()
                kget_temp()

                return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse('FORM IS NOT VALID!!!', status=400)
    else:
        f = TempsForm(initial={
            't_low': config_yaml['treshold_low'],
            't_high': config_yaml['treshold_high']
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


def get_csv_period(request):
    response = HttpResponse(content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(
        datetime.datetime.now().strftime('%A-%d-%B-%Y')
    )
    with open('temps.csv', mode='r') as rf:
        response.write(rf.read())
    return response
