from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User 
from django.utils import timezone
from .models import Chat
import openai
from chatbot.settings import OPENAI_API_KEY

# Create your views here. HTML pages, database info, etc. anything you want users to view
openai_api_key = OPENAI_API_KEY
openai.api_key = openai_api_key

def ask_openai(message):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "You are a helpful assistant who is friendly and provides responses no more than 100 words unless otherwise instructed."}, # Change content to adjust ChatGPT's approach/angle/expertise
            {"role": "user", "content": message}
        ]
    )
    print(response)
    answer = response.choices[0].message['content'].strip()
    return answer

@login_required(login_url='login')
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats}) 

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2: 
            try:
                user = User.objects.create_user(username, None, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except: 
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Passwords don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')