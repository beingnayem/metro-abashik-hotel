from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def signin(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    
    else:
        if request.method=='POST':
            email= request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Account not found! Incorrect e-mail or password")
                return redirect('signin')

    return render(request, 'accounts/signin.html')


@login_required
def signout(request):
    logout(request)
    return redirect('signin')
