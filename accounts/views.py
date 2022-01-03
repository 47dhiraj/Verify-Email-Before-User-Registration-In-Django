from django.contrib.auth import login, authenticate
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from accounts.models import Profile
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.template.loader import render_to_string

from .forms import SignUpForm
from .tokens import account_activation_token
import requests



def home_view(request):
    return render(request, 'accounts/home.html')



def profile_view(request):
    username = request.user.username
    email = request.user.email
    confirmation = request.user.profile.signup_confirmation

    context = {'username': username, 'email': email, 'confirmation': confirmation}
    return render(request, 'accounts/profile.html', context)



def activation_sent_view(request):
    return render(request, 'accounts/activation_sent.html')



def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('profile')
    else:
        return render(request, 'accounts/activation_invalid.html')



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            api_key = 'your_api_key'   
                                                        
            response = requests.get(
                "https://isitarealemail.com/api/email/validate",  
                params={'email': email},                                        
                headers={'Authorization': "Bearer " + api_key})                 

            status = response.json()['status']                          

            if status == "valid":
                user = form.save()
                user.refresh_from_db()
                user.profile.first_name = form.cleaned_data.get('first_name')
                user.profile.last_name = form.cleaned_data.get('last_name')
                user.profile.email = form.cleaned_data.get('email')
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                subject = 'Please Activate Your Account'
                message = render_to_string('accounts/activation_request.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)  
                return redirect('activation_sent')

            else:
                return HttpResponse("Email address you provided does not exist ! Please provide a valid email address.")

    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})
