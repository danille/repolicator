from django.shortcuts import render, redirect


# Create your views here.
def index(request):
    return render(request, 'core/index.html')


def replicate(request):
    social = request.user.social_auth.get(provider='github')
    token = social.extra_data['access_token']
    print(token)
    return redirect('index')
