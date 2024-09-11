import json

from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
from django.views.decorators.csrf import csrf_exempt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI2MDkxMjg0LCJpYXQiOjE3MjYwMDQ4ODQsImp0aSI6ImVjMzdhZWNhYTg2MzRlMmM5MDgzYzRkZWFhYTY4NmFhIiwidXNlcl9pZCI6MX0.pvKHNkOFs0q5709LbVAkM1Q45RI8vTWbxOkoD4-6n0w"

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

#QR CODE VIEWS: STARTS


from django.shortcuts import render
from django.http import JsonResponse
import requests

@csrf_exempt
def qrcode_home(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        download_link = request.POST.get('download_link') == 'on'

        api_url = 'http://167.71.39.190:8000/api/qr-code/'
        headers = {'Content-Type': 'application/json'}
        body = {'data': data, 'download_link': download_link}

        response = requests.post(api_url, json=body, headers=headers)

        if response.status_code == 200:
            # Eğer download_link varsa JSON dönmeli, görsel değil
            try:
                response_data = response.json()
                if 'download_url' in response_data:
                    # Linki döndürüyoruz
                    return JsonResponse({
                        'message': 'QR code generated successfully.',
                        'download_url': response_data['download_url']
                    })
            except json.JSONDecodeError:
                # Eğer JSON döndüremiyorsa, görsel dönüyor demektir
                return HttpResponse(
                    response.content,  # Görsel içeriğini direkt döndür
                    content_type='image/png'
                )

        else:
            return JsonResponse({'error': 'QR code generation failed'}, status=500)

    return render(request, 'qrcode/home.html')

#QR CODE VIEWS: ENDS

#QUIC NOTE VIEWS: STARTS


def quicknote_home(request):
    return render(request, 'quicknote/home.html')


#QUICK NOTE VIEWS: ENDS

#IMAGE TO PDF VIEWS: STARTS


def imagetopdf_home(request):
    if request.method == 'POST':
        files = request.FILES.getlist('image_paths')

        if not files:
            return JsonResponse({'error': 'No files were uploaded'}, status=400)

        api_url = 'http://167.71.39.190:8000/api/imagetopdf/'
        headers = {
            'Authorization': f'Bearer {token}'
        }

        files_dict = [('image_paths', (file.name, file, file.content_type)) for file in files]
        response = requests.post(api_url, files=files_dict, headers=headers)

        if response.status_code == 201:
            response_data = response.json()
            return JsonResponse({
                'download_url': response_data.get('download_url', '')
            })
        else:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {'error': 'Unknown error occurred'}

            return JsonResponse({'error': f'PDF generation failed: {error_data.get("error", "Unknown error")}'},
                                status=response.status_code)

    return render(request, 'imagetopdf/home.html')

#IMAGE TO PDF VIEWS: ENDS
