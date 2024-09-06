from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests


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

        bearer_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1NjIzOTA5LCJpYXQiOjE3MjU2MjAzMDksImp0aSI6ImMzOWRhZWE3YTZjZTRjNDQ5MDZiOTcxZTJkNjc2ZTkxIiwidXNlcl9pZCI6MX0.Iab2HfSzdVLenDY9C7LHtbxjrBz-EVewotDxTCsDmQM'
        api_url = 'http://167.71.39.190:8000/api/create_short_url/'
        headers = {
            'Authorization': f'Bearer {bearer_token}',
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
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1NjI3ODIwLCJpYXQiOjE3MjU2MjQyMjAsImp0aSI6IjFjNDNjMmZlNmQzNjQ4OGFiMDE5MjI3MGEzYzcwYTk4IiwidXNlcl9pZCI6MX0.iX1xVdxs-SK3CZOo8rSGJmOG_Tp2FukQ4bVGt7mv8vo"

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
    API_URL = 'http://167.71.39.190:8000/api/urls/'
    headers = {
        'Authorization': f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1NjI4OTMwLCJpYXQiOjE3MjU2MjUzMzAsImp0aSI6IjQwNjQxZjI3YWViZTQ3MWM5ZjE1ZTJmMGMyMDJlOThhIiwidXNlcl9pZCI6MX0.27ves2E0kQ7SRl4uY0xEMf9vBK3ZC5D97_s28idgy6E',
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



#URL SHORTENER VIEWS: ENDS

