import json

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect
import requests
from django.views.decorators.csrf import csrf_exempt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI2OTE2NzQ0LCJpYXQiOjE3MjY4MzAzNDQsImp0aSI6IjI3NDMwNWIyMThhOTRkNTE5MzBlN2FiMjdkN2ZjMjViIiwidXNlcl9pZCI6Nn0.C3sKYntuU0LEwxcfnAymCOJJLGQTY7K5TS2-WLlBzhU"


# USER VIEWS: STARTS

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        response = requests.post(f'http://167.71.39.190:8000/api/register/',
                                 json={'username': username, 'password': password})
        if response.status_code == 201:
            return redirect('login')
        elif response.status_code == 400 and response.json().get('error') == 'User already exists':
            error_message = 'This username is used.'
            return render(request, 'user/register.html', {'error': error_message})
        else:
            return render(request, 'user/register.html', {'error': 'An error occurred. Please try again.'})
    return render(request, 'user/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        response = requests.post(f'http://167.71.39.190:8000/api/login/',
                                 json={'username': username, 'password': password})
        if response.status_code == 200:
            request.session['username'] = username
            return redirect('home')
        else:
            error_message = response.json().get('message', 'Invalid login informations.')
            return render(request, 'user/login.html', {'error': error_message})
    return render(request, 'user/login.html')


def logout_view(request):
    response = requests.post(f'http://167.71.39.190:8000/api/logout/')
    if response.status_code == 200:
        request.session.flush()
        return redirect('login')
    return HttpResponse(f"Error: {response.json().get('message')}", status=response.status_code)

# USER VIEWS: ENDS


# MAIN PAGES VIEWS: STARTS


def home(request):
    username = request.session.get('username', 'Guest')
    return render(request, 'main/main_page.html', {'username': username})


# MAIN PAGES VIEWS: ENDS


# URL SHORTENER VIEWS: STARTS


def url_home(request):
    if request.user.is_authenticated:
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
    else:
        return redirect('login')



@login_required(login_url='/login/')
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


def activate_url(request, short_url):
    API_URL = 'http://167.71.39.190:8000/api/update_activity/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.put(
        f'{API_URL}{short_url}/',
        json={'is_active': True},
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


# URL SHORTENER VIEWS: ENDS

# QR CODE VIEWS: STARTS

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
            try:
                response_data = response.json()
                if 'download_url' in response_data:
                    return JsonResponse({
                        'message': 'QR code generated successfully.',
                        'download_url': response_data['download_url']
                    })
            except json.JSONDecodeError:
                return HttpResponse(
                    response.content,
                    content_type='image/png'
                )

        else:
            return JsonResponse({'error': 'QR code generation failed'}, status=500)

    return render(request, 'qrcode/home.html')


# QR CODE VIEWS: ENDS

# QUIC NOTE VIEWS: STARTS


def quicknote_home(request):
    if request.method == 'POST':
        send_to = request.POST.get('send_to')
        text = request.POST.get('text')
        file = request.FILES.get('file')

        if not send_to or (not text and not file):
            return render(request, 'quicknote/home.html', {'error': 'You must provide either text or a file.'})

        api_url = 'http://167.71.39.190:8000/api/notes/'

        if not token:
            return render(request, 'quicknote/home.html', {'error': 'You are not authenticated.'})

        headers = {
            'Authorization': f'Bearer {token}',
        }

        data = {
            'send_to': send_to,
        }

        if text:
            data['text'] = text

        files = {}
        if file:
            files['file'] = file

        try:
            if files:
                response = requests.post(api_url, data=data, files=files, headers=headers)
            else:
                response = requests.post(api_url, data=data, headers=headers)

            if response.status_code == 201:
                return render(request, 'quicknote/home.html', {'success': True})
            else:
                error_message = response.json().get('detail', 'Something went wrong.')
                return render(request, 'quicknote/home.html', {'error': error_message})

        except requests.exceptions.RequestException as e:
            return render(request, 'quicknote/home.html', {'error': 'An error occurred while making the request.'})

    return render(request, 'quicknote/home.html')


def sent_notes_view(request):
    api_url = 'http://167.71.39.190:8000/api/notes/sent/'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        notes = response.json()
    else:
        notes = []

    return render(request, 'quicknote/sent_notes.html', {'notes': notes})


def received_notes_view(request):
    api_url = 'http://167.71.39.190:8000/api/notes/received/'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        notes = response.json()
    else:
        notes = []

    return render(request, 'quicknote/received_notes.html', {'notes': notes})


def sent_note_detail_view(request, note_id):
    api_url = f'http://167.71.39.190:8000/api/notes/sent/'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        notes = response.json()
        note = next((item for item in notes if item['id'] == note_id), None)
        return render(request, 'quicknote/sent_notes_detail.html', {'note': note})
    else:
        return render(request, 'quicknote/sent_notes_detail.html', {'note': None})


def received_note_detail_view(request, note_id):
    api_url = f'http://167.71.39.190:8000/api/notes/received/'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        notes = response.json()
        note = next((item for item in notes if item['id'] == note_id), None)
        return render(request, 'quicknote/received_notes_detail.html', {'note': note})
    else:
        return render(request, 'quicknote/received_notes_detail.html', {'note': None})


# QUICK NOTE VIEWS: ENDS

# IMAGE TO PDF VIEWS: STARTS


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
            pdf_url = response_data.get('download_url', '')

            return JsonResponse({
                'preview_url': pdf_url
            })
        else:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {'error': 'Unknown error occurred'}

            return JsonResponse({'error': f'PDF generation failed: {error_data.get("error", "Unknown error")}'},
                                status=response.status_code)

    return render(request, 'imagetopdf/home.html')


# IMAGE TO PDF VIEWS: ENDS

def get_user_from_api(request):
    query = request.GET.get('send_to', '')
    if query:
        api_url = f'http://167.71.39.190:8000/autocomplete/users/?send_to={query}'
        res = requests.get(api_url)
        if res.status_code == 200:
            users = res.json()
        else:
            users = []
    else:
        users = []

    return render(request, 'partials/user_list.html', {'users': users})
