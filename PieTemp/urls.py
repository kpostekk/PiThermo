"""PieTemp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from collector import views as co_views

urlpatterns = [
    path('', co_views.dashboard_view, name='home'),
    path('settings/', co_views.settings_view, name='settings'),
    path('temperature/', co_views.raw_temp, name='raw temp'),
    path('r/set-mode/<int:mode>/', co_views.set_relay, name='set relay'),
    path('r/get-mode/', co_views.get_relay_status, name='get relay'),
    path('r/toggle/', co_views.switch_relay, name='toggle relay'),
    path('history/', co_views.get_csv_period, name='history'),
    path('json/', co_views.jsonify_statuses, name='json'),
    path('m/clear-log/', co_views.clear_switch_log)
]
