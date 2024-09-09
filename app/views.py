from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1ODcyMTA5LCJpYXQiOjE3MjU4Njg1MDksImp0aSI6Ijc1MWRjZmNkYmIyMjQ0N2I4ODA3MjE3YjUxZmJjY2FkIiwidXNlcl9pZCI6MX0.vig3nasjLere-ReAzypcSUBlGqPaLfQZEAmypLErVXA"

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

#URL SHORTENER VIEWS: ENDS

