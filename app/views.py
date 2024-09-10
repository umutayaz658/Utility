from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1ODgwOTc1LCJpYXQiOjE3MjU4NzczNzUsImp0aSI6IjY1ZmJkYmYxNmFjNjQ4YzJiZTM3MzUyODI3OTdiMWMwIiwidXNlcl9pZCI6MX0.1A9iG3o4hXa8c9oBmYTFFdi6rHpl4i1wRhi-kYXmhK4"

# MAIN PAGES VIEWS: STARTS


def home(request):
    return render(request, 'main/main_page.html')


#MAIN PAGES VIEWS: ENDS


#URL SHORTENER VIEWS: STARTS

def url_home(request):
    short_url = None
    if request.method == 'POST':
        long_url = request.POST.get('long_url')
        validity_period = request.POST.get('validity_period')
        one_time_only = request.POST.get('one_time_only') == 'on'
        password = request.POST.get('password')

        api_url = 'http://167.71.39.190:8000/api/create_short_url/'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = {
            'long_url': long_url,
            'validity_period': validity_period,
            'is_active': True,
            'one_time_only': one_time_only,
            'password': password
        }

        response = requests.post(api_url, json=data, headers=headers)
        if response.status_code == 201:
            short_url = response.json().get('short_url')
        else:
            short_url = 'Error'

    return render(request, 'url/home.html', {'short_url': short_url})


def user_urls(request):
    api_url = "http://167.71.39.190:8000/api/urls/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        urls = response.json()
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"API Error: {e}", status=500)

    return render(request, 'url/user_urls.html', {'urls': urls})


def deactivate_url(request, short_url):
    API_URL = 'http://167.71.39.190:8000/api/update_activity/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.put(
        f'{API_URL}{short_url}/',
        json={'is_active': False},
        headers=headers
    )

    if response.status_code == 200:
        return redirect('user_urls')
    else:
        return redirect('user_urls')


def delete_url(request, short_url):
    API_URL = 'http://167.71.39.190:8000/api/delete/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.put(
        f'{API_URL}{short_url}/',
        json={'is_deleted': True},
        headers=headers
    )

    if response.status_code == 200:
        return redirect('user_urls')
    else:
        return redirect('user_urls')


def update_validity_period(request, short_url):
    if request.method == 'POST':
        new_validity_period = request.POST.get('new_validity_date')
        new_validity_period = datetime.strptime(new_validity_period, '%Y-%m-%d %H:%M')
        formatted_validity_period = new_validity_period.isoformat()

        API_URL = 'http://167.71.39.190:8000/api/update_validity/'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.put(
            f'{API_URL}{short_url}/',
            json={'validity_period': formatted_validity_period},
            headers=headers
        )

        if response.status_code == 200:
            return redirect('user_urls')
        else:
            return redirect('user_urls')

#URL SHORTENER VIEWS: ENDS

